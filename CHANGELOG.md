# Kids First Release Coordinator Release 1.6.0

## Features

Support auth0 token validation.

### Summary

Feature Emojis: ⬆️x3 ♻️x1 ✅x1 🔧x1 ✨x1
Feature Labels: [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x4 [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x2 [devops](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/devops) x1

### New features and changes

- (#170) ⬆️ Bump django from 2.1.9 to 2.1.10 - @dependabot[bot]
- (#169) ⬆️ Bump django from 2.1.7 to 2.1.9 - @dependabot[bot]
- (#168) ⬆️ Upgrade urllib3 - @dankolbman
- (#165) ♻️ Refactor for getting db host from environment - @XuTheBunny
- (#164) ✅ Add test for unauthed user cannot access study releases - @XuTheBunny
- (#162) 🔧 Add netlify to CORS whitelist - @dankolbman
- (#160) ✨ Add auth0 token validation - @dankolbman


# Kids First Release Coordinator Release 1.5.3

## Features

### Summary

Feature Emojis: 🐛x6 ♻️x4 🔥x2 🔧x2 ✨x1 🙈x1 ⬆️x1 🐳x1
Feature Labels: [bug](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/bug) x8 [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x8 [devops](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/devops) x5 [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x1

### New features and changes

- (#159) ♻️ Read secrets as raw strings - @dankolbman
- (#158) 🐛 Fix typo in secret path - @dankolbman
- (#157) 🐛 Fix EGO settings - @XuTheBunny
- (#156) 🐛 Allow releases to re-enter cancelling state - @dankolbman
- (#155) ♻️ Store Ego service token for coordinator in cache - @XuTheBunny
- (#154) 🔥 Replace pep8 with codestyle - @dankolbman
- (#152) ♻️ Load secrets directly from vault - @dankolbman
- (#151) ✨ Store ego public key - @XuTheBunny
- (#147) 🐛 Fix static paths - @dankolbman
- (#148) 🐛 Update testing with correct apps - @dankolbman
- (#150) 🙈 Ignore ci files in jenkins - @dankolbman
- (#144) 🔧 Improve docker-compose for development - @dankolbman
- (#145) 🔥 Remove setup.cfg - @dankolbman
- (#143) 🔧 Refactor settings - @dankolbman
- (#138) ⬆️  Bump Django version - @dankolbman
- (#140) ♻️  App pytest.ini for quick access pytest - @XuTheBunny
- (#137) 🐳 Add dev stage to docker - @XuTheBunny
- (#133) 🐛 Improve compose for dev - @dankolbman

# Kids First Release Coordinator Release 1.5.2

## Features

### Summary

Feature Emojis: 🖼x1 🐛x1
Feature Labels: [documentation](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/documentation) x1

### New features and changes

- (#131) 🖼 Update logo - @dankolbman
- (#130) 🐛 Set default settings module for wsgi entry - @dankolbman

# Kids First Release Coordinator Release 1.5.1

## Features

### Summary

Feature Emojis: 🐳x1
Feature Labels: [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x1

### New features and changes

- (#127) 🐳 Docker refactor - @dankolbman

# Kids First Release Coordinator Release 1.5.0

## Features

### Summary

Feature Emojis: 📌x2 ✨x1 ⬆️x1 🔧x1
Feature Labels: [bug](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/bug) x3 [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x2 [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x1

### New features and changes

- (#122) ✨ Adds last_published fields to study model - @dankolbman
- (#126) ⬆️ Bump urllib3 dependency - @dankolbman
- (#125) 📌 Pin redis requirements - @dankolbman
- (#123) 📌 Set python to version 3.6 in Dockerfile - @dankolbman
- (#121) 🔧 Include jwt in Authorization header in requests to task's /status - @dankolbman


# Kids First Release Coordinator Release 1.4.0

## Features

Sends an Ego application JWT to task services so they may verify that the request originated from the coordinator

### Summary

Feature Emojis: ✨x1 ⬆️x1
Feature Labels: [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x1 [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x1

### New features and changes

- (#119) ✨ Add ego jwt - @dankolbman
- (#118) ⬆️ Upgrade requests dependency for vuln warning - @dankolbman

# Kids First Release Coordinator Release 1.3.0

## Features

### Summary

Feature Emojis: ✨x1 ✏️x1 ♻️x1 🔊x1 📝x1
Feature Labels: [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x2 [data model](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/data%20model) x1 [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x1 [devops](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/devops) x1 [documentation](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/documentation) x1

### New features and changes

- (#116) ✨ Release notes - @dankolbman
- (#115) ✏️ Coerce progress status from percent to int - @dankolbman
- (#114) ♻️ Use response content instead of json for log dumps - @dankolbman
- (#113) 🔊 Add failure logging - @dankolbman
- (#111) 📝 Add information on integrating services with the coordinator - @dankolbman


# Kids First Release Coordinator Release 1.2.1

## Features

Upgrade django to patch security vulnrability.

### Summary

Feature Emojis: ⬆️x1
Feature Labels: [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x1

### New features and changes

- (#109) ⬆️ Upgrade django version - @dankolbman

# Kids First Release Coordinator Release 1.2.0

## Features

Minor Bug fixes and updates.

### Summary

Feature Emojis: 🐛x2 👷x1 ✨x1
Feature Labels: [bug](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/bug) x2 [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x1 [documentation](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/documentation) x1

### New features and changes

- (#106) 🐛 Add missing return statement - @dankolbman
- (#103) 👷 Use module in Jenkinsfile - @dankolbman
- (#105) ✨ Filter by state - @dankolbman
- (#104) 🐛 Fix CircleCI badge in README - @dankolbman

# Kids First Release Coordinator Release 1.1.0

## Features

### Summary

Feature Emojis: 🐛x3 ✨x2 ✏️x1 ⚡️x1 🔧x1
Feature Labels: [bug](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/bug) x5 [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x1 [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x1 [devops](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/devops) x1

### New features and changes

- (#98) ✏️  s/published/complete/ - @dankolbman
- (#96) 🐛 Status check cancel release - @dankolbman
- (#95) ⚡️ Test refactoring - @dankolbman
- (#94) ✨ Check for staged and published states in task - @dankolbman
- (#93) 🐛 Increase study name size - @dankolbman
- (#85) ✨ Release Versions - @dankolbman
- (#90) 🐛 Fix model refactor - @dankolbman
- (#89) 🔧 Tune down numprocs to utilize less memory - @dankolbman


# Kids First Dataservice Release 1.0.0

## Features

### Summary

Feature Emojis: ✨x2 ♻️x2 🐛x2 📦x1 📝x1
Feature Labels: [refactor](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/refactor) x3 [feature](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/feature) x2 [bug](https://api.github.com/repos/kids-first/kf-api-release-coordinator/labels/bug) x2

### New features and changes

- (#81) 📦 Upgrade cryptography package - @dankolbman
- (#60) ✨ Add status checks - @dankolbman
- (#80) ✨ Add enabled filter to task services - @dankolbman
- (#72) ♻️ Harden task failures - @dankolbman
- (#78) 🐛  Don't allow release in canceling to be canceled again - @dankolbman
- (#77) 📝 Update docs with failure and cancelation info - @dankolbman
- (#71) 🐛 Handle timeouts from services - @dankolbman
- (#69) ♻️ Use django-fsm - @dankolbman
