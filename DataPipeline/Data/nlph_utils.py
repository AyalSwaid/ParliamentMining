"""
Utility functions to help with hebrew nlp
variables names formate:
    - starts with re_* means it is a regex expression
    - starts with rep* means it is a regex pattern (after compile regex expression)
"""


import re



re_letters = "[\u0590-\u05ea\s]"
re_any = "[-\u0590-\u05ea\s\w]"
re_table_contents = 'תוכן העניינים'
re_one_seder_yom = 'הצעות לסדר'
re_one_seder_yom2 = 'הצעה לסדר-היום'
re_kns_table_docs = 'מסמכים שהונחו על שולחן הכנסת'
re_kns_voting = 'הצבעה'
re_one_minute_talk = 'נאומים בני דקה'

re_bullshit_titles = [re_one_seder_yom2, re_table_contents, re_one_seder_yom, re_kns_table_docs, re_kns_voting, re_one_minute_talk]

re_plenum_start = ("הישיבה ה", "של הכנסת ה")
rep_plenum_start = re.compile(fr"\*\*הישיבה ה.*של הכנסת ה.*\*\*")

rep_title = re.compile(fr'\*\*.+\*\*')

rep_debate_title = re.compile("")

# is_MP_speaker = ""
rep_is_speaker = re.compile(fr'UU(.+)\s?\(?{re_letters}*\)?:UU')

rep_first_two_bills = re.compile("\*\*\(קריאה שנייה וקריאה שלישית\)\*\*")

