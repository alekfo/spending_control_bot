import sqlite3

def check_data(table):
    with sqlite3.connect('bot.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM `{table}`")
        result = cursor.fetchall()

        return result

if __name__ == "__main__":
    print(check_data('employees'))