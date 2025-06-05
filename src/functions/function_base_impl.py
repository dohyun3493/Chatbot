import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import mysql.connector
from config.config import Config
import os
import pymysql
from pymysql.cursors import DictCursor
import matplotlib.font_manager as fm
import platform

# 한글 폰트 설정 
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic') 


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

def generate_total_production_by_machine_chart(start_date, end_date, save_path=None):
    print("check3")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT machine_id, SUM(completed_qty) AS total_qty
        FROM production_data
        WHERE timestamp >= %s AND timestamp <= %s
          AND TIME(timestamp) = '18:00:00'
        GROUP BY machine_id
        ORDER BY machine_id;
    """

    try:
        cursor.execute(query, (start_date + ' 18:00:00', end_date + ' 18:00:00'))
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not data:
        return "No data found for the specified period."

    df = pd.DataFrame(data, columns=['machine_id', 'total_qty'])
    df['total_qty'] = df['total_qty'].astype(float)

    plt.figure(figsize=(10, 6))
    plt.plot(df['machine_id'], df['total_qty'], marker='o', linestyle='-', color='teal')

    for i, v in enumerate(df['total_qty']):
        plt.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=9)

    plt.title("Total Production by Machine")
    plt.xlabel("Machine ID")
    plt.ylabel("Total Completed Quantity")
    plt.grid(True)

    if save_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(base_dir, exist_ok=True)
        save_path = os.path.join(base_dir, "production_chart.png")

    plt.savefig(save_path)
    plt.close()
    print(f"Chart saved at {save_path}")

    return save_path


def generate_monthly_machine_comparison_chart(start_date, end_date, save_path=None):
    print("check4")
    
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT machine_id, DATE_FORMAT(timestamp, '%Y-%m') AS month, AVG(completed_qty) AS avg_qty
        FROM production_data
        WHERE timestamp >= %s AND timestamp <= %s
          AND TIME(timestamp) = '18:00:00'
        GROUP BY machine_id, DATE_FORMAT(timestamp, '%Y-%m')
        ORDER BY month, machine_id;
    """

    try:
        cursor.execute(query, (start_date + ' 18:00:00', end_date + ' 18:00:00'))
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not data:
        return "No data found for the specified period."

    df = pd.DataFrame(data, columns=['machine_id', 'month', 'avg_qty'])
    df['avg_qty'] = df['avg_qty'].astype(float)

    plt.figure(figsize=(12, 6))
    for machine_id in df['machine_id'].unique():
        machine_data = df[df['machine_id'] == machine_id]
        plt.plot(machine_data['month'], machine_data['avg_qty'], marker='o', label=machine_id)

    plt.title("Monthly Average Production by Machine")
    plt.xlabel("Month")
    plt.ylabel("Average Completed Quantity")
    plt.legend(title='Machine ID')
    plt.grid(True)
    plt.xticks(rotation=45)

    if save_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(base_dir, exist_ok=True)
        save_path = os.path.join(base_dir, "production_chart.png")

    plt.savefig(save_path)
    plt.close()
    print(f"Chart saved at {save_path}")

    return save_path

def generate_status_distribution_chart(start_date, end_date, save_path=None):
    print("check5")
    
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT production_status, COUNT(*) AS count
        FROM production_data
        WHERE timestamp >= %s AND timestamp <= %s
          AND TIME(timestamp) = '18:00:00'
        GROUP BY production_status;
    """

    try:
        cursor.execute(query, (start_date + ' 18:00:00', end_date + ' 18:00:00'))
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not data:
        return "No data found for the specified period."

    df = pd.DataFrame(data, columns=['production_status', 'count'])

    plt.figure(figsize=(6, 6))
    plt.pie(df['count'], labels=df['production_status'], autopct='%1.1f%%', startangle=140)
    plt.title("Production Status Distribution")

    if save_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(base_dir, exist_ok=True)
        save_path = os.path.join(base_dir, "production_chart.png")

    plt.savefig(save_path)
    plt.close()
    print(f"Chart saved at {save_path}")

    return save_path

def generate_monthly_total_production_chart(start_date, end_date, save_path=None):
    print("check_monthly_total")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT DATE_FORMAT(timestamp, '%Y-%m') AS `year_month`,
               SUM(completed_qty) AS total_production
        FROM production_data
        WHERE timestamp >= %s AND timestamp <= %s
          AND TIME(timestamp) = '18:00:00'
        GROUP BY `year_month`
        ORDER BY `year_month`;
    """

    try:
        cursor.execute(query, (start_date + ' 18:00:00', end_date + ' 18:00:00'))
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not data:
        return "No data found for the specified period."

    df = pd.DataFrame(data, columns=['year_month', 'total_production'])
    df['total_production'] = df['total_production'].astype(float)

    plt.figure(figsize=(10, 6))
    plt.plot(df['year_month'], df['total_production'], marker='o', linestyle='-', color='coral')
    plt.title(f"Monthly Total Production from {start_date} to {end_date}")
    plt.xlabel("Month")
    plt.ylabel("Total Production")
    plt.grid(True)
    plt.xticks(rotation=45)

    if save_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(base_dir, exist_ok=True)
        save_path = os.path.join(base_dir, "production_chart.png")

    plt.savefig(save_path)
    plt.close()
    print(f"Chart saved at {save_path}")

    return save_path

def generate_selected_months_production_comparison_chart(month_list, save_path=None):
    print("check_selected_months_comparison")

    if not month_list:
        return "Month list is empty."

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ', '.join(['%s'] * len(month_list))
    query = f"""
        SELECT DATE_FORMAT(timestamp, '%Y-%m') AS `month_label`,
               SUM(completed_qty) AS total_production
        FROM production_data
        WHERE DATE_FORMAT(timestamp, '%Y-%m') IN ({placeholders})
          AND TIME(timestamp) = '18:00:00'
        GROUP BY `month_label`
        ORDER BY `month_label`;
    """

    try:
        cursor.execute(query, month_list)
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not data:
        return "No data found for the specified months."

    df = pd.DataFrame(data, columns=['month_label', 'total_production'])
    df['total_production'] = df['total_production'].astype(float)

    plt.style.use('seaborn-v0_8-muted')
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')

    colors = plt.cm.Set2.colors[:len(df)] 
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df['month_label'], df['total_production'], color=colors, width=0.5)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.0f}', 
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

    ymin = df['total_production'].min() * 0.95
    ymax = df['total_production'].max() * 1.05
    plt.ylim(ymin, ymax)

    title_range = ", ".join(month_list)
    plt.title(f"Total Production Comparison: {title_range}", fontsize=14, fontweight='bold')
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Total Production", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    if save_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(base_dir, exist_ok=True)
        save_path = os.path.join(base_dir, f"production_chart.png")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Chart saved at {save_path}")

    return save_path