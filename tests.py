import re

string="<td>1.43XR</td>"
pattern='<td>(.*)XR</td>'

result = re.search(pattern, string)
if result and result.group and len(result.group()) > 0:
    value = float(result.group(1))
    print(value)