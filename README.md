# I-am-the-Law
Quick web search for German laws and corresponding verdicts

This script allows the user to specify a certain German law (e.g., ErbStG, AO, HGB, etc.) along with a section and paragraph, which will be printed in a GUI window.

The user can further search for verdicts of the jurisprudence regarding the section.

## Getting Laws

- If no section is provided, the structure of the law is printed
- If no paragraph is provided, the whole section is printed
- If you want to browse in a law that is not available in the dropdown menu, just type in its official abbreviation (note that some laws are not available on the website)

## Getting Verdicts
- If you have specified a law and a section, you can crawl verdicts regarding the respective section (this might take a while depending on the number of verdicts)
- A list of crawled verdicts will open in a new window
- You can select a verdict from the list and get a basic description with the "Worum geht's?" button
- You can filter the verdicts and their descriptions using regular expressions
- With the "Zum Urteil!" button, you are redirected to the full text of the selected verdict
