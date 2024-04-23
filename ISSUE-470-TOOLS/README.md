# Brief overview of the different components related to [issue #470](https://github.com/cf-convention/cf-convention.github.io/issues/470)

Essentially this commit provide the tools to update all the already published Standard Name Table `xml` files according to the format changes outlined in 
[issue #457](https://github.com/cf-convention/cf-convention.github.io/issues/457).

Updating the xml files to the new format is carried out in two steps, where the first step implements the format changes and the second step adds some missing elements that are required according to the xml schema specification. None of these change the material content of the standard name table entries. I.e. the standard names and their description, etc. are not impacted. 

The tools and some helper functions are located in the new subdirectory `ISSUE-470-TOOLS`, which also holds log files and other informational files.


**The following workflow were used to process the xml files**

1. The python program `step1.py` is executed:
    > python step1.py > step1.log

    which implements the format changes. First it reads the xml file and immediately saves a "backup copy" with the string "__ORIGINAL" added to the file name. If the backup copy already exists, the program uses it as input and writes to the "normal" xml file (i.e. not the backup version). The following changes are implemented and a detailed log are printed to the screen (i.e. standard output, which is piped to the log file).
    - "Header section"*
        - Add as first line the xml declaration `<?xml version="1.0"?>` if not already present.
        - Update the xml schema reference to `xsi:noNamespaceSchemaLocation="https://cfconventions.org/Data/schema-files/cf-standard-name-table-2.0.xsd"`.
        - Add the new tag `<conventions>`.
        - Add the new tag `<first_published>` where the datetime is is transferred from the existing tag <last_modified>. <br/>
        For version 1 the datetime is taken from the published html web page.<br/>
        For version 71 add the seconds (`:00`) to the datetime.
        - Reuse the existing tag <last_modified> to hold the datetime when the file was processed.
    - *Standard name entries*
        - Whenever a standard name has a spurious `<space>` (or several) replace it with an underscore.
        - In version 12 delete first instance of exact duplicate entry for `sea_surface_height_above_reference_ellipsoid`.
    - *Alias entries*
        - Remove all aliases of standard names having spurious space(s) because they were corrected in the corresponding entries.
        - Change representation of multiple aliases (cf. issue [#509](https://github.com/cf-convention/cf-conventions/issues/509) for details).
        - Delete first instance of exact duplicate alias entries.

2. The python program `list_errors.py` is executed:

    > python list_errors.py >  step1-error-list.txt
    
    It reads the xml files and writes to standard output a list of xml syntax and schema errors in the input file. This is piped to the file `step1-error-list.txt`, which is manually inspected.

3. The python program `compact_errors.py` is executed:

    > python compact_errors.py step1-error-list.txt > step1-error-table.txt

    which produces a more compact overview of the different error types and in which versions they occur. The output file is manually inspected.

    From this inspection it is evident that in some table versions standard name entries sometimes lack required tags. 

4. The python program `step2.py` is executed:

    > python step2.py > step2.log

    which reads the "normal" xml files and writes back to the same file. It adds the required tags `<description>` and `<canonical_units>`  where either or both are missing in standard name entries. The added tags are empty. A detailed log is written to the screen (standard output, which is piped to the log file).

5. The python program `list_errors.py` is again executed:

    > python list_errors.py >  step2-error-list.txt
    
    The print output is piped to the file `step2-error-list.txt`, which is manually inspected.

6. The python program `compact_errors.py is again executed:

    > python compact_errors.py step2-error-list.txt > step2-error-table.txt

    which produces a more compact overview of the different error types and in which versions they occur. The outpout file is manually inspected. 

**From this inspection is is clear that the number and types of errors are greatly reduced.**

THe remaining errors are basically of two types:
* In version 26 several standard names were both defined and aliased. This is not accepted xml syntax (for the particular data type used). The details remains to be investigated.
* In addition, the duplicate entries identified in [issue #273](https://github.com/cf-convention/discuss/issues/273) remains. Once the definitive details for how to fix this has been established they should be implemented in `step1.py`


