# Feeding Protocol Doc

## Premise:

This project tackles the digitisation of the "Protocol for Standardised Parenteral Nutrition for Preterm Infants."
When preterm infants are born, the lack of nutrition influences growth and development which is essential in their care. The main problem is providing this support cot-side in the neo-natal unit (NNU). With a computer-based software application we can provide the important information clearly to the doctors and nurses so they can make the process more efficient and be able to
help in the nutritional management of the infants in the NNU.

### Stakeholders:

The following people are able to access your data and will be using the software.

- Study monitors

- The Research Ethics Committee (REC)

- Sponsor Representatives

These people will be able to view the patient's unencoded medical information revealing the patient by name. Encryption of personal information is necessary.

The biobank which will contain samples of the infants or mothers sample is governed by UCC and INFANT and both comply with the EU's GDPR laws. This means that the data must be pseudonymised.

## Goals:

The goal for this project is to make this version of the protocol simple as the existing form is a small piece of paper that clinicians must carry and reference.
This new project wants to abstract some elements of the protocol and make the form more readable. 

## Possibilities:

There is confusion on whether this application will communicate with MN-CMS via a REST API. This will not be decided on for a while but in the mean time, the basic concept of digitizing the protocol is simple and functionality for MN-CMS integration could be a factor during development.

There is the possibility of this being used in other hospitals also. Because of this, some concepts may need to be abstracted as these new hospitals may not be familiar with the protocols processes and conditions.

## Stack:

| Stage    | Tech stack               | Explination                                                                 |
| -------- | ------------------------ | --------------------------------------------------------------------------- |
| Frontend | React TS                 | TS for type safety + React is a solid framewok                              |
| Backend  | Python                   | Simple. Possibility for AI integration for advising.                        |
| Database | PostgreSQL               | Auditing, wide frameworks compatible and integrates well with FHIR servers. |
| Hosting  | Hosting on AWS Beanstalk | Flexible and CI/CD                                                          |

## Design:




