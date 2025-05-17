import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import mysql.connector
from config.config import Config
import os
import pymysql
from pymysql.cursors import DictCursor

def get_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT
    )

def generate_production_chart(start_date, end_date, save_path=None):
    print("check1")
    
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT DATE(timestamp) AS production_date, completed_qty
        FROM production_data
        WHERE timestamp >= %s AND timestamp <= %s
          AND TIME(timestamp) = '18:00:00'
        ORDER BY production_date;
    """

    try:
        cursor.execute(query, (start_date + ' 18:00:00', end_date + ' 18:00:00'))
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not data:
        return "No data found for the specified period."

    df = pd.DataFrame(data, columns=['production_date', 'completed_qty'])
    df['completed_qty'] = df['completed_qty'].astype(float)

    plt.figure(figsize=(10, 5))
    plt.bar(df['production_date'], df['completed_qty'], color='skyblue')
    plt.title("Daily Production Chart")
    plt.xlabel("Date")
    plt.ylabel("Production")
    plt.grid(axis='y')
    plt.xticks(rotation=45)

    if save_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(base_dir, exist_ok=True)
        save_path = os.path.join(base_dir, "production_chart.png")

    plt.savefig(save_path)
    plt.close()
    print(f"Chart saved at {save_path}")
    return save_path

def generate_monthly_average_production_chart(start_date, end_date, save_path=None):
    print("check2")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT DATE_FORMAT(timestamp, '%Y-%m') AS `year_month`,
               AVG(completed_qty) AS `avg_production`
        FROM production_data
        WHERE DATE(timestamp) BETWEEN %s AND %s
          AND TIME(timestamp) = '18:00:00'
        GROUP BY DATE_FORMAT(timestamp, '%Y-%m')
        ORDER BY DATE_FORMAT(timestamp, '%Y-%m');
    """

    cursor.execute(query, (start_date, end_date))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(data, columns=['year_month', 'avg_production'])

    df['avg_production'] = df['avg_production'].astype(float)

    if df.empty:
        return "No data found for the specified period."

    plt.figure(figsize=(12, 6))
    plt.plot(df['year_month'], df['avg_production'], marker='o', linestyle='-', color='mediumseagreen')

    for i, value in enumerate(df['avg_production']):
        plt.text(i, value, f'{value:.1f}', ha='center', va='bottom', fontsize=9)

    plt.title(f"Monthly Average Production from {start_date} to {end_date}")
    plt.xlabel("Month")
    plt.ylabel("Average Production")
    plt.grid(True)
    plt.xticks(rotation=45)

    ymin = df['avg_production'].min() * 0.95
    ymax = df['avg_production'].max() * 1.05
    plt.ylim(ymin, ymax)

    if save_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(base_dir, exist_ok=True)
        save_path = os.path.join(base_dir, "production_chart.png")

    plt.savefig(save_path)
    plt.close()
    print(f"Chart saved at {save_path}")

    return save_path