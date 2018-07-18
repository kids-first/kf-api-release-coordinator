# Semantic Versioning for Releases

## Motivation

Semantic versions, ie, versions numbers in the form `X.Y.Z`, are useful for
quickly comparing two sets of data and code and being able to tell their
relative recency. This document outlines how semantic versions will be
assigned to releases.

## Background

Currently, all releases are assigned a `kf_id` identifier with an `RE`
prefix. Although this is enough to distinguish individual versions,
it is not enough to tell whether where two versions sit in time
or compatability.


## Implementation


### Release Versioning Rules

The rules for versioning a release should be as follows:

The maximum, minor, and patch versions will be used as the basis for the
version of the next release. A release is any release initiated in the release
coordinator, regardless of its outcome.
From this this base version, a new version is issued on the following:

- A major version is issued for any release that has a shape change to the data
and involves, at least, all currently public studies
- A minor versio is issued for a release that is positevyl reviewed and
published to the portal
- A patch version is issued for all releases begun in the coordinator

Note that all releases begin with the next consecutive patch version number,
and are only *promoted* to a major or minor version upon publication.
This means that a given release will have its version *changed* after being
released. Task services will need to account for this as the final version
number will not be known until the `publishing` step.


### Portal Versioning Rules

An all-encompassing portal version is issued for every release based on
the same criteria as above.

## Examples

### Patch versioning for review process

For every candidate release between releases to the portal, the patch version will be bumped globally in the coordinator.
Note that none of these relases except the first and last rows are published to the portal.

| Notes                                      |  SD_1 |  SD_2 |  SD_3 | Data Version |
|--------------------------------------------|:-----:|:-----:|:-----:|:------------:|
| Initial Release                            | 1.0.0 | 1.0.0 | 1.0.0 |     1.0.0    |
| First candidate release                    | 1.0.1 |   -   |   -   |     1.0.1    |
| Second candidate release                   | 1.0.2 | 1.0.2 | 1.0.2 |     1.0.2    |
| Third candidate release                    | 1.0.3 |   -   | 1.0.3 |     1.0.3    |
| Fourth candidate release                   | 1.0.4 |   -   | 1.0.4 |     1.0.4    |
| Successfully release of Fourth candidate   | 1.1.0 | 1.1.0 | 1.1.0 |     1.1.0    |

*NB*: The last two versions are the same release!

### Major/Minor versioning in production

Each row represents a public release, some full portal releases that include all public studies with new data shape, some releases that include updates to all studies, and some releases that include some subset of all the public studies.


| Notes                    |  SD_1 |  SD_2 |  SD_3 | Data Version |
|--------------------------|:-----:|:-----:|:-----:|:------------:|
| First Release            | 1.0.0 | 1.0.0 | 1.0.0 |     1.0.0    |
| Updates to SD_1          | 1.1.0 |   -   |   -   |     1.1.0    |
| Updates to SD_1 and SD_2 | 1.2.0 | 1.2.0 |   -   |     1.2.0    |
| Updates to all studies   | 1.3.0 | 1.3.0 | 1.3.0 |     1.3.0    |
| Shape change, new portal | 2.0.0 | 2.0.0 | 2.0.0 |     2.0.0    |
