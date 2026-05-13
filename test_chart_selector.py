from modules.chart_selector import select_chart

test_cases = [
    ({"class_type": "Activity", "dimension": "1D"}, {"main_chart": "vwap_bar", "sub_charts": ["scatter_pf"]}),
    ({"class_type": "Activity", "dimension": "2D"}, {"main_chart": "dual_line", "sub_charts": ["switch_bar"]}),
    ({"class_type": "Activity", "dimension": "ND"}, {"main_chart": "turnover_bar", "sub_charts": ["timeline"]}),
]

for inputs, expected in test_cases:
    result = select_chart(inputs)
    print(f"Inputs: {inputs} | Result: {result} | Pass: {result == expected}")
