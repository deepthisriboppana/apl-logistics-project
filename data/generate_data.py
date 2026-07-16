import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)
N = 5000

shipping_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
delivery_statuses = ['Shipping on time', 'Late delivery', 'Advanced shipping', 'Shipping canceled']
markets = ['LATAM', 'Europe', 'Pacific Asia', 'USCA', 'Africa']
regions = {
    'LATAM': ['South America', 'Central America', 'Caribbean'],
    'Europe': ['Western Europe', 'Eastern Europe', 'Southern Europe'],
    'Pacific Asia': ['Southeast Asia', 'East Asia', 'Oceania'],
    'USCA': ['US Northeast', 'US Southeast', 'US West', 'Canada'],
    'Africa': ['West Africa', 'East Africa', 'North Africa'],
}
customer_segments = ['Consumer', 'Corporate', 'Home Office']
categories = ['Electronics', 'Clothing', 'Furniture', 'Office Supplies', 'Sports', 'Toys', 'Books', 'Food']
departments = ['Technology', 'Apparel', 'Furniture', 'Office', 'Outdoors', 'Fan Shop', 'Book Shop', 'Pet Shop']
order_statuses = ['Complete', 'Pending', 'On Hold', 'Payment Review', 'Processing', 'Closed', 'Suspected Fraud', 'Canceled']
payment_types = ['Debit', 'Credit', 'Transfer', 'Cash']

countries_by_market = {
    'LATAM': ['Mexico', 'Brazil', 'Argentina', 'Colombia', 'Chile'],
    'Europe': ['Germany', 'France', 'UK', 'Spain', 'Italy'],
    'Pacific Asia': ['China', 'Japan', 'India', 'Australia', 'Singapore'],
    'USCA': ['United States', 'Canada'],
    'Africa': ['Nigeria', 'Kenya', 'Egypt', 'South Africa', 'Ghana'],
}

cities_by_country = {
    'United States': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'Germany': ['Berlin', 'Hamburg', 'Munich', 'Frankfurt', 'Cologne'],
    'Brazil': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'],
    'China': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu'],
    'India': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'],
    'UK': ['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow'],
    'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
    'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
    'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey', 'Puebla', 'Cancun'],
    'Japan': ['Tokyo', 'Osaka', 'Kyoto', 'Nagoya', 'Sapporo'],
    'Nigeria': ['Lagos', 'Abuja', 'Kano', 'Ibadan', 'Port Harcourt'],
    'South Africa': ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Port Elizabeth'],
    'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
    'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'La Plata'],
    'Spain': ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao'],
    'Italy': ['Rome', 'Milan', 'Naples', 'Turin', 'Palermo'],
    'Colombia': ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena'],
    'Chile': ['Santiago', 'Valparaíso', 'Concepción', 'La Serena', 'Antofagasta'],
    'Kenya': ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret'],
    'Egypt': ['Cairo', 'Alexandria', 'Giza', 'Luxor', 'Aswan'],
    'Ghana': ['Accra', 'Kumasi', 'Tamale', 'Sekondi', 'Cape Coast'],
    'Singapore': ['Singapore'],
    'Spain': ['Madrid', 'Barcelona', 'Valencia'],
}

default_cities = ['Capital City', 'Port City', 'Main City', 'Central City', 'East City']

rows = []
start_date = datetime(2023, 1, 1)

for i in range(N):
    market = random.choice(markets)
    region = random.choice(regions[market])
    country = random.choice(countries_by_market[market])
    city_list = cities_by_country.get(country, default_cities)
    city = random.choice(city_list)
    segment = random.choice(customer_segments)
    ship_mode = random.choice(shipping_modes)

    scheduled = {'Standard Class': 5, 'Second Class': 3, 'First Class': 2, 'Same Day': 1}[ship_mode]
    delay_prob = {'Standard Class': 0.55, 'Second Class': 0.45, 'First Class': 0.30, 'Same Day': 0.20}[ship_mode]
    market_delay = {'LATAM': 0.1, 'Europe': -0.05, 'Pacific Asia': 0.08, 'USCA': -0.1, 'Africa': 0.15}[market]
    actual_delay = np.random.normal(delay_prob + market_delay, 0.3)
    real_days = max(1, int(scheduled + np.random.randint(-1, 3) * (1 if actual_delay > 0.4 else 0)))
    gap = real_days - scheduled
    late_risk = 1 if gap > 0 else 0

    if gap > 1:
        status = 'Late delivery'
    elif gap < 0:
        status = 'Advanced shipping'
    elif random.random() < 0.03:
        status = 'Shipping canceled'
    else:
        status = 'Shipping on time'

    order_date = start_date + timedelta(days=random.randint(0, 700))
    product_price = round(random.uniform(10, 500), 2)
    qty = random.randint(1, 10)
    discount_rate = round(random.uniform(0, 0.3), 2)
    discount = round(product_price * discount_rate, 2)
    item_total = round(product_price * qty * (1 - discount_rate), 2)
    profit_ratio = round(random.uniform(-0.1, 0.4), 3)
    profit = round(item_total * profit_ratio, 2)
    sales = round(item_total * random.uniform(0.9, 1.1), 2)
    benefit = round(profit * random.uniform(0.8, 1.2), 2)
    sales_per_customer = round(sales * random.uniform(1, 5), 2)
    lat = round(random.uniform(-60, 70), 4)
    lon = round(random.uniform(-180, 180), 4)
    category = random.choice(categories)
    department = random.choice(departments)

    rows.append({
        'Type': random.choice(payment_types),
        'Days for shipping (real)': real_days,
        'Days for shipment (scheduled)': scheduled,
        'Benefit per order': benefit,
        'Sales per customer': sales_per_customer,
        'Delivery Status': status,
        'Late_delivery_risk': late_risk,
        'Category Id': categories.index(category) + 1,
        'Category Name': category,
        'Customer City': city,
        'Customer Country': country,
        'Customer Fname': f'Customer{i}First',
        'Customer Id': 1000 + i,
        'Customer Lname': f'Customer{i}Last',
        'Customer Segment': segment,
        'Customer State': region,
        'Market': market,
        'Order City': city,
        'Order Country': country,
        'Order Customer Id': 1000 + i,
        'Order Item Discount': discount,
        'Order Item Discount Rate': discount_rate,
        'Order Item Product Price': product_price,
        'Order Item Profit Ratio': profit_ratio,
        'Order Item Quantity': qty,
        'Sales': sales,
        'Order Item Total': item_total,
        'Order Profit Per Order': profit,
        'Order Region': region,
        'Order State': region,
        'Order Status': random.choice(order_statuses),
        'Product Name': f'{category} Product {random.randint(1,50)}',
        'Product Price': product_price,
        'Shipping Mode': ship_mode,
        'Department Id': departments.index(department) + 1,
        'Department Name': department,
        'Latitude': lat,
        'Longitude': lon,
        'Order Date': order_date.strftime('%Y-%m-%d'),
    })

df = pd.DataFrame(rows)
df['Delay Gap'] = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
df['Delivery Class'] = df['Delay Gap'].apply(
    lambda x: 'Early' if x < 0 else ('On-Time' if x == 0 else 'Delayed')
)
df.to_csv('data/apl_logistics_data.csv', index=False)
print(f"Dataset generated: {len(df)} rows")
print(df.head(3))