# Developing a fuzzy search program for combining internal and external data

Whilst working in a start-up charity, marketing wanted to analyse external government data on education establishments against our own membership data. The objective was to identify how many members, fellows, and accredited teachers we had in each school, and potentially identify any headteacher / trust CEO already in membership that could be contacted for group membership at their school(s).
The challenge with this is that years of little to no data expertise in the organisation has meant much of the data is inconsistent. For example, a member types their place of work when joining rather than selecting from a pre-defined list, therefore there are variations such as CofE and COE or Church of England, not to mention any typos.

To resolve data inconsistency, fuzzywuzzy was used to implement fuzzy matching of strings:

"FuzzyWuzzy is a library of Python which is used for string matching. Fuzzy string matching is the process of finding strings that match a given pattern. Basically it uses Levenshtein Distance to calculate the differences between sequences." - https://www.geeksforgeeks.org/fuzzywuzzy-python-library/#:~:text=FuzzyWuzzy%20is%20a%20library%20of,calculate%20the%20differences%20between%20sequences.

The design of the program is made so that non-tech colleagues can follow a simple set of instructions to install Python and run the script via command line. 

In designing the solution, one of the challenges faced was computational complexity. There are many iterative tasks involved in the program which makes it quite a lengthy process... One of the ways I worked around this was by reducing the number of needed iterations via conditional filtering based on matching at least single token, using pattern matching: https://pandas.pydata.org/docs/reference/api/pandas.Series.str.contains.html

Further developments considered: cleaning school data on Salesforce by fuzzy matching against the government establishment database. Exploratory analysis of establishment attributes, looking to spot trends in group membership acquisition. Analytics on market penetration by establishment.
