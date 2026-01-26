
from extract_invoices import classify_content

# Content from the problematic invoice
test_string = "Thiết bị truyền dữ liệu băng rộng hoạt động trong băng tần 2.4 GHz và vô tuyến mạng diện rộng công suất thấp (LPWAN), Tapo H100, hiệu TP-LINK"

category = classify_content(test_string)
print(f"Content: {test_string}")
print(f"Category: {category}")

# Control test
test_string_2 = "Cơm gà xối mỡ"
print(f"Content: {test_string_2}")
print(f"Category: {classify_content(test_string_2)}")
