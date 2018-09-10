# DOI Assignment for Releases

## Motivation

DOIs provide a convenient format to cite and retrieve data.
A DOI would make a given release of data easy to reference and retrieve
by anyone utilizing Kids First Data.

## Background

Each release is given a kf_id and a semantic version.
These two identifiers are the canonical keys used to look up a given release
and should be used in the DOI.

## Uses

The DOI will be displayed alongside the release in the coordinator UI and
eventually, the data release archive.

It may also be desireable to include it in the portal in the footer with the
data version or with any downloads or manifests that are generated


## Implementation

Every *public* release shall be minted a new DOI.
This means any *major* or *minor* version number, as the versions are currently
implemented.

Each study in a release will also be given a DOI.

These DOIs will be minted using the `10.24370` prefix and a suffix containing
the release or study's kf_id followed by the semantic version and delimited by
an underscore.

The DOI will resolve to the portal until release bundles are created and made
available on the website.

The XML will include the following:

| Field                        |  Value                                                                                      |
|------------------------------|---------------------------------------------------------------------------------------------|
| identifier                   | The DOI identifier                                                                          |
| creators                     |                                                                                             |
| creators.creator             | One creator for each investigator in each study in the release                              |
| creators.creator.creatorName | Name of the investigator                                                                    |
| titles                       | Two titles for both kf_id and version                                                       |
| title                        | Kids First Data Resource Center Release <kf_id>                                             |
| title                        | Kids First Data Resource Center Release <version>                                           |
| publicationYear              | Year of publication                                                                         |
| dates.date                   | Date of release publish                                                                     |
| dates.date.dateType          | Available                                                                                   |
| publisher                    | Kids First Data Resource Center                                                             |
| resourceTypeGeneral          | Dataset                                                                                     |
| resourceType                 | Dataset/Genomic and clinical data                                                           |
| version                      | Semantic version of the release                                                             |
| relatedIdentifier            | One identifier for each study in the release, or the identifier for the release, if a study |
| relatedIdentifierType        | DOI                                                                                         |
| relationType                 | HasPart for each study, IsPart for the release                                              |

See the *release.xml* and *study.xml* files for examples.


## Examples

`10.24370/RE_00000000_0.1.0`

`10.24370/RE_00000000_2.9.0`

`10.24370/SD_BHJXBDQK_0_1.3.0`
