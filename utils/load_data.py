import sqlite3

def load_sql_data(db_path, queries):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    data = []
    for query in queries:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        data.extend([dict(zip(columns, row)) for row in rows])

    connection.close()
    return data


def format_data_for_chunks(data):
    """Format product and review data into text."""
    formatted_texts = []

    product_text = ""
    review_text = ""

    for item in data:
        if 'product_name' in item:
            product_text += (f"Product ID: {item.get('product_id', '')}\n"
                             f"Product Name: {item.get('product_name', '')}\n"
                             f"Description: {item.get('description', '')}\n"
                             f"Price: {item.get('price', '')}\n"
                             f"Category: {item.get('category', '')}\n"
                             f"Brand: {item.get('brand', '')}\n"
                             f"Stock Quantity: {item.get('stock_quantity', '')}\n"
                             f"Rating: {item.get('rating', '')}\n"
                             f"Release Date: {item.get('release_date', '')}\n"
                             f"Supplier: {item.get('supplier', '')}\n\n")
        elif 'comment' in item:
            review_text += (f"Review ID: {item.get('review_id', '')}\n"
                            f"Product ID: {item.get('product_id', '')}\n"
                            f"Rating: {item.get('rating', '')}\n"
                            f"Comment: {item.get('comment', '')}\n\n")

    if product_text:
        formatted_texts.append(product_text)
    if review_text:
        formatted_texts.append(review_text)

    return formatted_texts