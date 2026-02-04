"""
Test parsing of multi-line abstract in RIS file
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.parser import parse_ris_file

# Create a sample RIS file with multi-line abstract (using user's example)
ris_content = """TY  - JOUR
AB  - Abstract. Risk of bias (RoB) assessment of randomized clinical trials (RCTs) is 
vital to conducting systematic reviews. Manual RoB assessment for hundreds of 
RCTs is a cognitively demanding, lengthy process and is prone to subjective 
judgment. Supervised machine learning (ML) can help to accelerate this process but 
requires a hand-labelled corpus. There are currently no RoB annotation guidelines 
for randomized clinical trials or annotated corpora. In this pilot project, we test the 
practicality of directly using the revised Cochrane RoB 2.0 guidelines for 
developing an RoB annotated corpus using a novel multi-level annotation scheme. 
We report inter-annotator agreement among four annotators who used Cochrane 
RoB 2.0 guidelines. The agreement ranges between 0% for some bias classes and 
76% for others. Finally, we discuss the shortcomings of this direct translation of 
annotation guidelines and scheme and suggest approaches to improve them to obtain 
an RoB annotated corpus suitable for ML.
TI  - First steps towards a risk of bias corpus of randomized controlled trials
ER  - 
"""

with open('test_multiline.ris', 'w', encoding='utf-8') as f:
    f.write(ris_content)

print("=" * 70)
print("TEST: Multi-line Abstract Parsing")
print("=" * 70)

try:
    df = parse_ris_file('test_multiline.ris')
    
    if df.empty:
        print("Error: No references parsed")
    else:
        ref = df.iloc[0]
        abstract = ref.get('abstract', '')
        print(f"Parsed Abstract Length: {len(abstract)}")
        print(f"Abstract Content Preview:\n{abstract[:200]}...")
        
        # Check if it contains text from the second line
        if "vital to conducting systematic reviews" in abstract:
            print("\n✓ PASS: Abstract contains text from second line")
        else:
            print("\n✗ FAIL: Abstract is truncated at the first line")
            print("  Missing: 'vital to conducting systematic reviews'")

except Exception as e:
    print(f"Error parsing file: {e}")

import os
if os.path.exists('test_multiline.ris'):
    os.remove('test_multiline.ris')
