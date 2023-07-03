# S.C.A.M.P
## SOC Calculation And Mapping Program
SCAMP automatically maps the right SOC to a physical location.



## Release Notes
### version 0.1 - "Laziness is the essence of contemplation"
### 20230703
SCAMP is a Midwest Solutions Engineering Skunkworks project.

SCAMP ingests .csv files containing physical locations, and geolocates
those locations using zip code. Your data must contain a column
named 'zip', and that column must contain US zip codes. 

It can receive multiple input files in a single email, processing and returning each in a separate email.

Very little in the way of error and file handling in this release.

## Immediate Task:
* Find a home for the script to run

### Follow on Tasks (unordered):
* error detection replies via email with instructions
* ingest xlsx
* flexibility in zipcode inputs (variations on column name, GPT column validation/preprocessing?)
* break file processing operations into a separate class
* * thread/background process (non-blocking operation
