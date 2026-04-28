# Shiny Deployment Deep Dive

Choose a deployment target based on auth needs, regulatory posture, and how
many concurrent users you expect. Every target requires a reproducible
environment via `renv` — without a lockfile your build is one CRAN release
away from breaking.

## Target decision table

| Target                       | Auth model                              | Scaling                                  | Regulated-env fit       | Cost                                     |
|------------------------------|-----------------------------------------|------------------------------------------|-------------------------|------------------------------------------|
| Posit Connect                | SAML / OAuth / LDAP, per-content ACLs   | Multi-process, autoscaling per content   | Strong (validated)      | Commercial license, on-prem or hosted    |
| shinyapps.io                 | Public; password (paid tiers)           | Worker pools, app-level limits           | Weak — not for PHI      | Free tier; usage-based paid plans        |
| Docker + ShinyProxy          | LDAP / OAuth / Keycloak / SAML          | Container per session, k8s autoscaling   | Strong (self-hosted)    | Open source; infra + ops cost            |
| Shiny Server (Open Source)   | None (front with NGINX + auth proxy)    | Single process per app — does not scale  | Weak                    | Free, but legacy                          |
| Shiny Server Pro (legacy)    | LDAP / Active Directory / PAM           | Multi-process per app                    | Moderate (deprecated)   | Commercial; superseded by Connect        |

## `renv` is universal

Every deployment requires a lockfile. Run this once per project, commit the
lockfile, and re-snapshot whenever dependencies change.

```r
renv::init()
renv::snapshot()
```

Run `renv::status()` before every deploy to confirm the lockfile matches the
library. All four production targets (Connect, shinyapps.io, ShinyProxy via
Dockerfile, Shiny Server via image) restore from `renv.lock`.

## Posit Connect

Recommended for regulated, clinical, or enterprise use.

- Publish from RStudio or programmatically:
  ```r
  rsconnect::deployApp(
    account = "<connect>",
    server = "connect.example.com"
  )
  ```
- For git-deployment / CI workflows, generate a manifest:
  ```r
  rsconnect::writeManifest()
  ```
  Connect picks up `manifest.json` + `renv.lock` from the repo on push.
- Environment variables: set them under the content's settings panel —
  never commit secrets to the app source.
- Validated environments: pin R + package versions via Connect's environment
  manager combined with `renv.lock`. The same image rebuilds on every deploy.
- Auth: SAML, OAuth (Google / Azure AD / Okta), and LDAP integrate at the
  server level; per-content access lists restrict viewers/collaborators.
- Schedules: Connect renders Quarto and R Markdown alongside Shiny, so
  upstream ETL reports and downstream dashboards live in one place.

## shinyapps.io

Quick public publishing for prototypes, demos, and open data work.

- One-time setup:
  ```r
  rsconnect::setAccountInfo(
    name = "my_account",
    token = "<token>",
    secret = "<secret>"
  )
  ```
- Deploy from the project root:
  ```r
  rsconnect::deployApp()
  ```
- Slug rules: app name 3–63 characters, lowercase alphanumeric plus hyphens.
- Free tier: 5 apps, 25 active hours/month, public-only.
- Paid tiers: password protection, custom domains, more active hours, and
  additional worker processes — but still not appropriate for clinical PHI
  or any data subject to HIPAA / GDPR Article 9 / GxP.

## Docker + ShinyProxy

Self-hosted, containerised, and the cleanest fit for on-prem deployments
where you control the infrastructure.

- Generate the dockerfile from a `golem`-based app:
  ```r
  golem::add_dockerfile_shinyproxy()
  ```
- Pin the base image, use a multi-stage build, and copy only the renv
  lockfile + app source:
  ```dockerfile
  FROM rocker/shiny-verse:4.4.1
  COPY renv.lock /app/renv.lock
  WORKDIR /app
  RUN R -e "renv::restore()"
  COPY . /app
  CMD ["R", "-e", "options(shiny.port=3838); my_app::run_app()"]
  ```
- Configure ShinyProxy with `application.yml`:
  ```yaml
  proxy:
    title: My Shiny Apps
    authentication: ldap
    ldap:
      url: ldap://ldap.internal:389
      user-dn-pattern: "uid={0},ou=people,dc=example,dc=com"
    specs:
      - id: my-app
        container-image: my-org/my-app:1.0.0
        container-cmd: ["R", "-e", "options(shiny.port=3838); my_app::run_app()"]
  ```
- Auth: LDAP, OAuth (Google / GitHub / Okta), Keycloak, and SAML are all
  first-class citizens.
- Scaling: ShinyProxy launches a container per session by default. Tune
  `max-instances` per spec, and run on Kubernetes for cluster autoscaling.

See `golem.md` for the matching `golem::add_dockerfile()` workflow.

## Shiny Server (Open Source)

Configure apps via `/etc/shiny-server/shiny-server.conf`; place app
directories under `/srv/shiny-server/`. There is no built-in auth — front
with NGINX plus an auth proxy (oauth2-proxy, Authelia) for anything beyond
local-trusted-network use. Single-process per app means it does not scale
beyond a handful of concurrent users. Treat as legacy: new on-prem work
should target ShinyProxy or Connect.

## Async deployments

```r
library(promises)
library(future)
plan(multisession, workers = 4)
```

Required when any reactive performs I/O > 200ms — database queries, API
calls, large file reads. Without `future` + `promises`, a single slow
reactive blocks every concurrent session on the same worker. Wrap the
slow call in `future_promise({ ... })` and chain results with `then()`.

## Logging

| Platform                    | Where logs live                                  |
|-----------------------------|--------------------------------------------------|
| Posit Connect               | Built-in log viewer per content                  |
| shinyapps.io                | `rsconnect::showLogs()` from the project         |
| Docker + ShinyProxy         | `docker logs <container>` (per-session container)|
| Shiny Server (Open Source)  | `/var/log/shiny-server.log`                      |

App-level: enable `options(shiny.error.log = TRUE)` so stack traces hit the
platform log instead of being swallowed by the reactive graph.

## Scaling notes

- Workers: Connect and ShinyProxy both scale horizontally — set worker
  counts based on observed concurrent users, not guesses.
- Autoscale rules: in Kubernetes, scale ShinyProxy on CPU or active-session
  count; in Connect, set min/max processes per content.
- Container resource limits: pin CPU and memory to prevent one runaway
  session from starving the host.
- In-process caching: `bindCache()` memoises a reactive within one R
  process — fine for single-worker apps, useless across workers.
- Cross-session caching: use `cachem::cache_redis()` (or `cache_disk()`
  on a shared volume) so all workers hit the same cache.

## Validated / regulated checklist (clinical)

When deploying for clinical or GxP use, the audit trail begins at deploy
time. Required artifacts:

| Artifact                            | Why                                                    |
|-------------------------------------|--------------------------------------------------------|
| `renv.lock`                         | Reproducible package set, version-pinned               |
| Version-pinned base image           | OS + system libs reproducible (e.g. `rocker/shiny-verse:4.4.1`) |
| Deployment audit trail              | Who deployed which version when (Connect history / CI) |
| Qualified package source            | e.g. Posit Package Manager validated snapshots         |
| Authenticated user log              | Who accessed which screen, captured at the proxy       |
| Source code repository URL in app   | Embedded in footer for traceability back to commit     |

See `teal.md` for additional regulated-deployment patterns specific to
clinical-trial review apps, and `testing.md` — CI must run the full test
suite (including `shinytest2` snapshots) before any deploy reaches a
validated environment.
