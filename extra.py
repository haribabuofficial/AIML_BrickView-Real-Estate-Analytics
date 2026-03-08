import numpy as np
import pandas as pd

import mysql.connector          # pip install mysql-connector-python
import streamlit as st    
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid

from PIL import Image
import plotly.express as px


import warnings
warnings.filterwarnings("ignore", category=UserWarning)
# connection

import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Iphone6+',
    database='project_1'
)

mycursor = mydb.cursor()


st.set_page_config(layout='wide')


# --------------------------------------------------------------------------------------------------------------

                                                # sidebar
# st.sidebar.header('Filters')
with st.sidebar:
    select = option_menu("Main Menu", ['Home', 'Data Exploration', 'SQL Queries', 'CRUD'])

# --------------------------------------------------------------------------------------------------------------
                                                # Home
if select == "Home":
    
    st.header("BRICKVIEW: REAL ESTATE ANALYTICS PLATFORM")
    
    images = Image.open('./media/images_2.png')
    st.image(images)

    st.header("About")
    st.write("")
    st.write("""We help buyers, investors, and real estate professionals make smarter, data-informed decisions by turning complex market data into clear, actionable insights. Our platform reveals what’s selling, which property types are in demand, and how pricing trends vary across regions and neighborhoods—so you can move with confidence instead of guesswork.""")
    st.write("")
    st.write("""From tracking sales performance to monitoring time-on-market trends, we give agents and teams the visibility they need to refine strategies and close deals faster. Whether you’re evaluating investment opportunities, pricing listings more accurately, or exploring new markets, our tools provide a reliable, data-backed view of the real estate landscape to support every decision you make.""")



# --------------------------------------------------------------------------------------------------------------

                                                # Data Exloration
if select == 'Data Exploration':
    # City- Multi-select
    cities = pd.read_sql("SELECT DISTINCT City FROM listing", mydb)
    # print(cities['City'].tolist())
    selected_cities = st.sidebar.multiselect("Select City", cities['City'].tolist())


    # Property type Dropdown
    property_types = pd.read_sql("SELECT DISTINCT Property_Type FROM listing", mydb)
    # print(property_types['Property_Type'].tolist())
    selected_property = st.sidebar.selectbox("Property Type", ['All'] + property_types['Property_Type'].tolist())


    # Price Range Slider
    price_range = st.sidebar.slider("Price Range", 100000, 5000000, (100000, 1000000), step=100000)


    # Agent - searchable dropdown
    agents = pd.read_sql("SELECT DISTINCT Agent_ID FROM listing", mydb)
    # print(agents['Agent_ID'].tolist())
    selected_agent = st.sidebar.selectbox("Agent", ["All"] + agents['Agent_ID'].tolist())


# --------------------------------------------------------------------------------------------------------------

                                            # Dataframe of sidebar
    query = """
            SELECT l.*, a.Name
            FROM listing l
            LEFT JOIN agents a 
                ON l.Agent_ID = a.Agent_ID
            WHERE 1=1
        """

    params = []

    # Cities
    if selected_cities:
        placeholder = ",".join(["%s"] * len(selected_cities))
        query += f" AND l.City IN ({placeholder})"
        params.extend(selected_cities)

    # Property Type
    if selected_property != "All":
        query += " AND l.Property_Type = %s"
        params.append(selected_property)

    # Price Range
    query += " AND l.Price BETWEEN %s AND %s"
    params.extend(price_range)

    # Agent
    if selected_agent != "All":
        query += " AND l.Agent_ID = %s"
        params.append(selected_agent)

    # print(params)

    # debug
    # st.write(query)
    # st.write(params)

    df = pd.read_sql(query, mydb, params = params)


# --------------------------------------------------------------------------------------------------------------


    tab1, tab2, tab3, tab4, tab5= st.tabs(["***GEOSPATIAL VISUALIZATION***","***Listing & Price of City***", "***Property Type Distribution***", "***Trend of Monthly Sales***", "***Table View***"])
    with tab5:
        st.subheader("Listings Table")
        # st.dataframe(df,use_container_width = True)
        # from st_aggrid import AgGrid

        AgGrid(
            df,
            pagination=True,
            paginationPageSize=20
        )

        st.download_button('DOWNLOAD', df.to_csv())



# # --------------------------------------------------------------------------------------------------------------

                                         # Interactive Map
    with tab1:                                    
        st.subheader("Property Map")

        fig_map = px.scatter_mapbox(df, 
                                    lat='Latitude', 
                                    lon='Longitude', 
                                    hover_name='City', 
                                    hover_data=['Price', 'Property_Type'], 
                                    zoom=4, 
                                    height=500, 
                                    mapbox_style='open-street-map')
        st.plotly_chart(fig_map, use_container_width=True)



# # --------------------------------------------------------------------------------------------------------------


                                    # Listing by City (Bar Chart)
    with tab2:
        st.subheader("Listing by City")

        city_count = df.groupby("City")['Listing_ID'].count().reset_index()

        print(city_count)

        fig_bar = px.bar(city_count,
                        x='City',
                        y='Listing_ID')
                        #  title="Number of Listings")

        st.plotly_chart(fig_bar, use_container_width=True)


                                            # Average Price by City (Bar Chart)
        st.subheader("Avg Price of City")

        avg_price = df.groupby("City")['Price'].mean().reset_index()

        print(avg_price)

        fig_bar = px.bar(avg_price,
                        x='City',
                        y='Price')

        st.plotly_chart(fig_bar, use_container_width=True)


# # --------------------------------------------------------------------------------------------------------------


                                    # Property Distribution (Pie chart)
    with tab3:
        st.subheader("Property Type Distribution")

        pie_query = """
            SELECT City, COUNT(*) as Count
            FROM listing
            WHERE 1=1
        """

        params = []

        # Property Type filter
        if selected_property != "All":
            pie_query += " AND Property_Type = %s"
            params.append(selected_property)

        # City filter
        if selected_cities:
            placeholder = ",".join(["%s"] * len(selected_cities))
            pie_query += f" AND City IN ({placeholder})"
            params.extend(selected_cities)

        pie_query += " GROUP BY City"

        pie_city = pd.read_sql(pie_query, mydb, params=params)

        if pie_city.empty:
            st.warning("No data available for selected filters.")
        else:
            fig = px.pie(
                pie_city,
                names="City",
                values="Count",
                title=f"{selected_property} - Listings Across Cities" if selected_property != "All" else "Listings Across Cities"
            )
            st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------

        st.subheader("Property Type Distribution by City")
        # st.write(df["Property_Type"].unique())

        pie_query = """
            SELECT City, Property_Type, COUNT(*) as Count
            FROM listing
            WHERE 1=1
        """
        params = []

        if selected_cities:
            placeholder = ",".join(["%s"] * len(selected_cities))
            pie_query += f" AND City IN ({placeholder})"
            params.extend(selected_cities)

        pie_query += " GROUP BY City, Property_Type"

        pie_city = pd.read_sql(pie_query, mydb, params=params)


        if selected_cities:
            cols = st.columns(len(selected_cities))
        
            for i, city in enumerate(selected_cities):
                
                city_df = pie_city[pie_city["City"] == city]
                
                if not city_df.empty:
                    
                    property_dist = (city_df["Property_Type"].value_counts().reset_index())
                    
                    property_dist.columns = ["Property_Type", "Count"]
                    
                    fig = px.pie(
                        property_dist,
                        names="Property_Type",
                        values="Count",
                        title=f"{city} - Property Type Distribution"
                    )
                    
                    cols[i].plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data available for {city}")
        else:
            st.info("Please select at least one city")

# --------------------------------------------------------------------------------------------------------------


                                    # Monthly Trend (line chart)
    with tab4:
        st.subheader("Monthly Listing Trend")

        df['Date_Listed'] = pd.to_datetime(df['Date_Listed'])
        monthly = df.groupby(df['Date_Listed'].dt.to_period("M")).size()
        monthly = monthly.reset_index(name='Count')
        monthly['Date_Listed'] = monthly['Date_Listed'].astype(str)

        fig_line = px.line(
            monthly,
            x="Date_Listed",
            y="Count"
        )

        st.plotly_chart(fig_line, use_container_width=True)


# --------------------------------------------------------------------------------------------------------------


# SQL Query

if select == 'SQL Queries':
    tab1, tab2, tab3, tab4 = st.tabs(['📊 Property & Pricing Analysis', '⏱️ Sales & Market Performance', '🧑‍💼 Agent Performance', '🧍 Buyer & Financing Behavior'])
    

    property_questions = [
        "1. What is the average listing price by city?",
        "2. What is the average price per square foot by property type?",
        "3. How does furnishing status impact property prices?",
        "4. Do properties closer to metro stations command higher prices?",
        "5. Are rented properties priced differently from non-rented ones?",
        "6. How do bedrooms and bathrooms affect pricing?",
        "7. Do properties with parking and power backup sell at higher prices?",
        "8. How does year built influence listing price?",
        "9. Which cities have the highest median property prices?",
        "10. How are properties distributed across price buckets?"
    ]

    sales_questions = [
        "1. What is the average days on market by city?",
        "2. Which property types sell the fastest?",
        "3. What percentage of properties are sold above listing price?",
        "4. What is the sale-to-list price ratio by city?",
        "5. Which listings took more than 90 days to sell?",
        "6. How does metro distance affect time on market?",
        "7. What is the monthly sales trend?",
        "8. Which properties are currently unsold?"
    ]

    agent_questions = [
        "1. Which agents have closed the most sales?",
        "2. Who are the top agents by total sales revenue?",
        "3. Which agents close deals fastest?",
        "4. Does experience correlate with deals closed?",
        "5. Do agents with higher ratings close deals faster?",
        "6. What is the average commission earned by each agent?",
        "7. Which agents currently have the most active listings?"
    ]

    buyer_questions = [
        "1. What percentage of buyers are investors vs end users?",
        "2. Which cities have the highest loan uptake rate?",
        "3. What is the average loan amount by buyer type?",
        "4. Which payment mode is most commonly used?",
        "5. Do loan-backed purchases take longer to close?"
    ]


    with tab1:
        st.subheader("📊 Property & Pricing Analysis")
        selected_q = st.selectbox("Choose a question", property_questions)


        if selected_q == property_questions[0]:
            query = """
                        SELECT City, ROUND(AVG(Price)) AS Avg_Price 
                        FROM listing
                        GROUP BY City
                        ORDER BY Avg_Price DESC;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for city, avg_price in rows:
            #     print(city, avg_price)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns=c))


        if selected_q == property_questions[1]:
            query = """
                        SELECT Property_Type, ROUND(AVG(Price / Sqft)) AS Avg_Price_per_Sqft
                        FROM listing
                        GROUP BY Property_Type
                        ORDER BY Avg_Price_per_Sqft
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in values:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns=c))


        if selected_q == property_questions[2]:
            query = """
                        SELECT pa.Furnishing_Status, ROUND(AVG(l.Price)) AS Avg_Price
                        FROM listing l
                        INNER JOIN property_attributes pa
                            ON l.Listing_ID = pa.Listing_ID
                        GROUP BY pa.Furnishing_Status
                        ORDER BY Avg_Price DESC;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))   

        
        if selected_q == property_questions[3]:    
            query = """
                        SELECT 
                            CASE
                                WHEN pa.Metro_Distance_Km <= 1 THEN '<= 1 KM'
                                WHEN pa.Metro_Distance_Km > 1 AND pa.Metro_Distance_Km <=3 THEN '1-3 KM'
                                WHEN pa.Metro_Distance_Km > 3 AND pa.Metro_Distance_Km <=5 THEN '3-5 KM'
                                WHEN pa.Metro_Distance_Km > 5 AND pa.Metro_Distance_Km <=10 THEN '5-10 KM'
                                WHEN pa.Metro_Distance_Km > 10 AND pa.Metro_Distance_Km <=15 THEN '10-15 KM'
                            END AS Distance,
                            ROUND(AVG(l.Price)) AS Avg_Price
                        FROM Listing l
                        INNER JOIN Property_Attributes pa
                            ON l.Listing_ID = pa.Listing_ID
                        GROUP BY Distance
                        ORDER BY Avg_Price;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns=c))

        
        if selected_q == property_questions[4]:
            query = """
                        SELECT 
                            CASE
                                WHEN pa.Is_Rented = 0 THEN 'Not Rented'
                                WHEN pa.Is_Rented = 1 THEN 'Rented'
                            END AS Rented_Status,
                            ROUND(AVG(l.Price), 2) AS Avg_Price
                        FROM Listing l
                        INNER JOIN Property_Attributes pa
                            ON l.Listing_ID = pa.Listing_ID
                        GROUP BY Rented_Status
                        ORDER BY Avg_Price;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns=c))  


        if selected_q == property_questions[5]:   
            query = """
                        SELECT pa.Bedrooms AS No_of_Bedrooms, pa.Bathrooms AS No_of_Bathrooms, ROUND(AVG(l.Price)) AS Avg_Price
                        FROM Listing l
                        INNER JOIN Property_Attributes pa
                            ON  l.Listing_ID = pa.Listing_ID
                        GROUP BY pa.Bedrooms, pa.Bathrooms
                        ORDER BY pa.Bedrooms;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j, k in r:
            #     print(i, j, k)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))


        if selected_q == property_questions[6]:
            query = """
                        SELECT 
                            CASE 
                                WHEN pa.Parking_Available = 0 THEN 'Not Available'
                                ELSE 'Available' 
                            END AS Parking,
                            CASE
                                WHEN pa.Power_Backup = 0 THEN 'Not Available'
                                ELSE 'Available'
                            END AS Power_Backup,
                            ROUND(AVG(l.Price)) AS Avg_Price
                        FROM Listing l
                        INNER JOIN Property_Attributes pa
                            ON l.Listing_ID = pa.Listing_ID
                        GROUP BY Parking, Power_Backup
                        ORDER BY Avg_Price;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j, k, in r:
            #     print(i, j, k)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns= c))            


        if selected_q == property_questions[7]:
            query = """
                        SELECT pa.Year_Built, ROUND(AVG(l.Price),2) AS Avg_Price
                        FROM Listing l
                        INNER JOIN Property_Attributes pa
                            ON l.Listing_ID = pa.Listing_ID
                        GROUP BY pa.Year_Built
                        ORDER BY pa.Year_Built
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))


        if selected_q == property_questions[8]:
            query = """
                        with ordered_price AS (
                            SELECT 
                                City,
                                Price,
                                ROW_NUMBER() OVER(PARTITION BY City ORDER BY Price) AS rn,
                                COUNT(*) OVER(PARTITION BY City) AS cnt
                            FROM listing
                        )
                        SELECT
                            City,
                            ROUND(AVG(Price)) as Median_Price
                        FROM ordered_price
                        WHERE rn IN (FLOOR((cnt+1)/2), FLOOR((cnt+2) /2))
                        GROUP BY City;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))

        
        if selected_q == property_questions[9]:
            query = """
                        SELECT 
                            CASE
                                WHEN Price BETWEEN 1000000 AND 2000000 THEN '100K-200K'
                                WHEN Price BETWEEN 2000001 AND 3000000 THEN '200K-300K'
                                WHEN Price BETWEEN 3000001 AND 4000000 THEN '300K-400K'
                                WHEN Price BETWEEN 4000001 AND 5000000 THEN '400K-500K'
                                ELSE '500K+'
                            END AS Price_Bucket,
                            COUNT(*) AS Total_Properties
                        FROM Listing
                        GROUP BY Price_Bucket
                        ORDER BY 
                            CASE Price_Bucket
                                WHEN '100K-200K' THEN 1
                                WHEN '200K-300K' THEN 2
                                WHEN '300K-400K' THEN 3
                                WHEN '400K-500K' THEN 4
                                ELSE 5
                            END;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i in r:
            #     print(i)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))            


    with tab2:
        st.subheader("⏱️ Sales & Market Performance")
        selected_q = st.selectbox("Choose a question", sales_questions)

        if selected_q == sales_questions[0]:
            query = """
                        SELECT 
                            l.City,
                            ROUND(AVG(s.Days_on_Market)) AS Avg_Days_on_Market
                        FROM Listing l
                        INNER JOIN Sales s
                            ON l.Listing_ID = s.Listing_ID
                        GROUP BY l.City
                        ORDER BY Avg_Days_on_Market
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns=c))    


        if selected_q == sales_questions[1]:
            query = """
                        SELECT 
                            l.Property_Type,
                            ROUND(AVG(s.Days_on_Market)) AS Avg_Days_on_Market
                        FROM Listing l
                        INNER JOIN Sales s
                            ON l.Listing_ID = s.Listing_ID
                        GROUP BY l.Property_Type
                        ORDER BY Avg_Days_on_Market
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns=c))        
        
        
        if selected_q == sales_questions[2]:
            query = """
                        WITH percentage_price AS (
                            SELECT 
                                l.City,
                                CASE
                                    WHEN s.Sale_Price > l.Price THEN 1
                                    ELSE 0
                                END AS price_above_listing
                            FROM listing l
                            INNER JOIN sales s
                                ON l.Listing_ID = s.Listing_ID
                        )
                        SELECT
                            City,
                            ROUND(100 * SUM(price_above_listing) / COUNT(*), 2) AS sold_above_listing_price
                        FROM percentage_price
                        GROUP BY City
                        ORDER BY sold_above_listing_price DESC;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            # for i, j in r:
            #     print(i, j)

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns=c))


        if selected_q == sales_questions[4]:
            query = """
                SELECT 
                    l.Listing_ID, l.City, l.Property_Type, s.Days_on_Market
                FROM Listing l
                INNER JOIN Sales s
                    ON l.Listing_ID = s.Listing_ID
                WHERE s.Days_on_Market >= 90
                ORDER BY s.Days_on_Market DESC;
                """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))


        if selected_q == sales_questions[5]:
            query = """
                        SELECT 
                            CASE
                                WHEN pa.Metro_Distance_Km <= 1 THEN '<= 1 KM'
                                WHEN pa.Metro_Distance_Km > 1 AND pa.Metro_Distance_Km <=3 THEN '1-3 KM'
                                WHEN pa.Metro_Distance_Km > 3 AND pa.Metro_Distance_Km <=5 THEN '3-5 KM'
                                WHEN pa.Metro_Distance_Km > 5 AND pa.Metro_Distance_Km <=10 THEN '5-10 KM'
                                WHEN pa.Metro_Distance_Km > 10 AND pa.Metro_Distance_Km <=15 THEN '10-15 KM'
                            END AS Distance,
                            ROUND(AVG(s.Days_on_Market)) AS Avg_Day_on_Market
                        FROM sales s
                        INNER JOIN property_attributes pa
                            ON s.Listing_ID = pa.Listing_ID
                        GROUP BY Distance
                        ORDER BY Distance
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))        


        if selected_q == sales_questions[6]:
            query = """
                        SELECT 
                            DATE_FORMAT(s.Date_Sold, '%Y-%m') AS Sale_Month,
                            COUNT(*) AS Sales_Count,
                            ROUND(AVG(s.Sale_Price)) AS Avg_Sales
                        FROM sales s
                        GROUP BY Sale_Month
                        ORDER BY Sale_Month;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))

        
        if selected_q == sales_questions[7]:
            query = """
                        SELECT
                            l.Property_Type,
                            COUNT(*) AS unsold
                        FROM listing l
                        LEFT JOIN sales s
                            ON l.Listing_ID = s.Listing_ID
                        WHERE s.Listing_ID IS NULL
                        GROUP BY l.Property_Type
                        ORDER BY unsold;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))


    with tab3:
        st.subheader("🧑‍💼 Agent Performance")
        selected_q = st.selectbox("Choose a question", agent_questions)

        if selected_q == agent_questions[0]:
            query = """
                        SELECT Agent_ID, Name, Deals_Closed 
                        FROM agents
                        ORDER BY Deals_Closed DESC LIMIT 1;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))   


        if selected_q == agent_questions[1]:
            query = """
                        WITH agent_revenue AS(
                            SELECT 
                                a.Agent_ID, 
                                a.Name,
                                SUM(s.Sale_Price) AS total_sales_revenue,
                                COUNT(s.Listing_ID) AS total_sales_count
                            FROM agents a
                            INNER JOIN listing l
                                ON a.Agent_ID = l.Agent_ID
                            INNER JOIN sales s
                                ON l.Listing_ID = s.Listing_ID
                            GROUP BY a.Agent_ID, a.Name
                            ORDER BY total_sales_revenue DESC
                        ),
                        ranked_agents AS (
                        SELECT 
                            Agent_ID,
                            Name,
                            total_sales_revenue,
                            total_sales_count,
                            DENSE_RANK() OVER(ORDER BY total_sales_revenue DESC) AS Dense_Ranking
                        FROM agent_revenue
                        )
                        SELECT * 
                        FROM ranked_agents
                        WHERE Dense_Ranking <= 5;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))   


        if selected_q == agent_questions[2]: 
            query = """
                        SELECT Agent_ID, Name, Avg_Closing_Days
                        FROM agents
                        ORDER BY Avg_Closing_Days LIMIT 5;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))

        
        if selected_q == agent_questions[3]:
            query = """
                        SELECT
                            (
                                COUNT(*) * SUM(Experience_Years * Deals_Closed)
                                - SUM(Experience_Years) * SUM(Deals_Closed)
                            ) /
                            SQRT(
                                (COUNT(*) * SUM(Experience_Years * Experience_Years)
                                - POW(SUM(Experience_Years), 2)) *
                                (COUNT(*) * SUM(Deals_Closed * Deals_Closed)
                                - POW(SUM(Deals_Closed), 2))
                            ) AS Correlation_Experience_and_Deals_
                        FROM agents;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))

        
        if selected_q == agent_questions[4]:
            query = """
                        SELECT 
                            CASE
                                WHEN Rating >=1 AND Rating <=2 THEN '1-2'
                                WHEN Rating > 2 AND Rating <=3 THEN '2-3'
                                WHEN Rating > 3 AND Rating <= 4 THEN '3 - 4'
                                WHEN Rating > 3.5 AND Rating <= 4 THEN '3.5 - 4'
                                WHEN Rating > 4 AND Rating <= 4.5 THEN '4 -4.5'
                                WHEN Rating > 4.5 AND Rating <= 5 THEN '4.5 - 5'
                            END AS Rating_Range,
                            AVG(Avg_Closing_Days) AS Avg_Close_Days
                        FROM agents
                        GROUP BY rating_range
                        ORDER BY rating_range DESC;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))    


        if selected_q == agent_questions[5]:
            query = """
                        SELECT 
                            a.Agent_ID,
                            a.Name,
                            ROUND((s.Sale_Price * a.Commission_Rate) / 100) AS Commission_price
                        FROM agents a
                        INNER JOIN listing l
                            ON a.Agent_ID = l.Agent_ID
                        INNER JOIN sales s
                            ON l.Listing_ID = s.Listing_ID
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))   


        if selected_q == agent_questions[6]:
            query = """
                        SELECT 
                            a.Agent_ID,
                            a.Name,
                            COUNT(l.Listing_ID) AS Active_Listings
                        FROM agents a
                        INNER JOIN listing l
                            ON a.Agent_ID = l.Agent_ID
                        LEFT JOIN sales s
                            ON l.Listing_ID = s.Listing_ID
                        WHERE s.Listing_ID IS NULL
                        GROUP BY a.Agent_ID
                        ORDER BY Active_Listings DESC LIMIT 10;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))                 

    with tab4:
        st.subheader("🧍 Buyer & Financing Behavior")
        selected_q = st.selectbox("Choose a question", buyer_questions)


        if selected_q == buyer_questions[0]:
            query = """
                        SELECT 
                            Buyer_Type,
                            COUNT(*) AS Count,
                            ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS Percentage
                        FROM buyers
                        GROUP BY Buyer_Type;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))            


        if selected_q == buyer_questions[1]:
            query = """
                        SELECT 
                            l.City,
                            SUM(b.Loan_Taken) AS Number_of_Loan
                        FROM buyers b
                        INNER JOIN sales s
                            ON b.Sale_ID = s.Listing_ID
                        INNER JOIN listing l
                            ON s.Listing_ID = l.Listing_ID
                        GROUP BY l.City
                        ORDER BY Number_of_Loan DESC;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))

        
        if selected_q == buyer_questions[2]:
            query = """
                        SELECT 
                            Buyer_Type,
                            ROUND(AVG(Loan_Amount)) AS Avg_Loan_Amount
                        FROM Buyers
                        GROUP BY Buyer_Type;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))         


        if selected_q == buyer_questions[3]:
            query = """
                        SELECT
                            Payment_Mode,
                            COUNT(Payment_Mode) AS Payment_Method
                        FROM buyers
                        GROUP BY Payment_Mode
                        ORDER BY Payment_Method DESC;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))


        if selected_q == buyer_questions[4]:
            query = """
            
                        SELECT 
                            CASE 
                                WHEN b.Loan_Taken = 1 THEN 'Loan Buyers'
                                ELSE 'Non-Loan Buyers'
                            END AS Buyer_Financing_Type,
                            COUNT(*) AS Buyers_Count,
                            ROUND(AVG(s.Days_on_Market)) AS Avg_days_on_Market
                        FROM buyers b
                        INNER JOIN sales s
                            ON b.sale_Id = s.Listing_ID
                        GROUP BY Buyer_Financing_Type
                        ORDER BY Buyer_Financing_Type;
                    """

            mycursor.execute(query)

            r = mycursor.fetchall()

            c = [i[0] for i in mycursor.description]

            st.dataframe(pd.DataFrame(r, columns = c))            


    
# --------------------------------------------------------------------------------------------------------------

                                            # CRUD

if select == 'CRUD':
    menu = st.sidebar.selectbox('Select', ['CREATE', 'READ', 'UPDATE', 'DELETE'])

# ----------------------------------------------------------

    if menu == 'CREATE':
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Listings", "Property Attributes", "Agents", "Sales", "Buyers"])


        with tab1:
        
            st.subheader("Listing Details")

            listing_id = st.text_input("Listing ID")
            city = st.selectbox("City",['New York', 'Los Angeles', 'Houston', 'Phoenix', 'Chicago'], index=None, placeholder="Select a City")
            property_type = st.selectbox("Property Type", ["Apartment", "Villa", "House"], index=None, placeholder="Select a Property Type")
            price = st.number_input("Price", min_value=0)
            sqft = st.number_input("Square Feet", min_value=0)
            date_listed = st.date_input("Date Listed", key='date_listed')
            agent_id = st.text_input("Agent ID")
            latitude = st.number_input("Latitude", format="%.6f")
            longitude = st.number_input("Longitude", format="%.6f")
        
            if st.button('Submit', key='submit_listing'):
                query = """
                            INSERT INTO listing (Listing_ID, City, Property_Type, Price, Sqft, Date_Listed, Agent_ID, Latitude, Longitude) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """ 
                val = (listing_id, city, property_type, price, sqft, date_listed, agent_id, latitude, longitude)
                mycursor.execute(query, val)
                mydb.commit()            
                
                st.success("Listing submitted successfully!")


        with tab2:

            st.subheader("Property Attributes Details")

            query = """
                SELECT DISTINCT(Listing_ID)
                FROM listing;
            """
            distinct_listing_id = pd.read_sql(query, mydb)
            distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()
            # st.write(len(distinct_listing_id))

            listing_id = st.selectbox("Listing ID", distinct_listing_id, index=None, placeholder="Select a Listing ID", key="listing_id_1")
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=8)
            bathrooms = st.number_input("Bathrooms", min_value=0, max_value=8)
            floor_number = st.number_input("Floor Number", min_value=0)
            total_floors = st.number_input("Total Floors", min_value=0)
            year_built = st.number_input("Year Built", min_value=1900, max_value=2026)
            is_rented = st.checkbox("Is Rented?")
            tenant_count = st.number_input("Tenant Count", min_value=0)
            furnishing_status = st.selectbox("Furnishing Status", ["Furnished", "Unfurnished", "Semi-Furnished"])
            metro_distance = st.number_input("Metro Distance (km)", min_value=0.0)
            parking = st.checkbox("Parking Available?")
            power_backup = st.checkbox("Power Backup?")
            
            if st.button('Submit', key='submit_Property_Attributes'):
                query = """
                            INSERT INTO property_attributes (Listing_ID, Bedrooms, Bathrooms, Floor_Number, Total_Floors, Year_Built, Is_Rented , Tenant_Count, Furnishing_Status, Metro_Distance_km, Parking_Available, Power_Backup)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                val = (listing_id, bedrooms, bathrooms, floor_number, total_floors, year_built, is_rented, tenant_count, furnishing_status, metro_distance, parking, power_backup)
                mycursor.execute(query, val)
                mydb.commit()            

                st.success("Property Attributes submitted successfully!")


        with tab3:
            st.subheader("Agents Details")

            query = """
                SELECT DISTINCT(Agent_ID)
                FROM listing;
            """
            distinct_agent_id = pd.read_sql(query, mydb)
            distinct_agent_id = distinct_agent_id['Agent_ID'].tolist()

            agent_id = st.selectbox("Agent ID", distinct_agent_id, index=None, placeholder="Select a Listing ID", key = "agent_id_1")
            name = st.text_input("Name")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            commission_rate = st.number_input("Commission Rate (%)", min_value=0)
            deals_closed = st.number_input("Deals Closed", min_value=0)
            rating = float(st.slider("Rating (0-5)", min_value=1.0, max_value=5.0, step=0.1))
            experience_years = st.number_input("Experience (Years)", min_value=0)
            avg_closing_days = st.number_input("Avg Closing Days", min_value=0)

            if st.button('Submit', key='submit_agents'):

                query = """
                            INSERT INTO agents (Agent_ID, Name, Phone, Email, Commission_Rate, Deals_Closed, Rating, Experience_Years, Avg_Closing_Days)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                val = (agent_id, name, phone, email, commission_rate, deals_closed, rating, experience_years, avg_closing_days)
                mycursor.execute(query, val)
                mydb.commit()            
                                        
                st.success("Agent submitted successfully!")

        
        with tab4:

            st.subheader("Sales Details")
            query = """
                SELECT l.Listing_ID
                FROM listing l
                LEFT JOIN sales s
                ON s.Listing_ID = l.Listing_ID
                WHERE s.Listing_ID IS NULL;
            """
            sales_listing_id = pd.read_sql(query, mydb)
            sales_listing_id = sales_listing_id['Listing_ID'].tolist()     

            listing_id = st.selectbox("Listing ID", sales_listing_id, index=None, placeholder="Select a Listing ID", key="listing_id_2")
            sale_price = st.number_input("Sale Price", min_value=0)
            date_sold = st.date_input("Date Sold", key='date_sold')

            query = """
                SELECT Date_Listed
                FROM listing
                WHERE Listing_ID = %s
            """
            params = []

            if listing_id:
                params = [listing_id]
                df = pd.read_sql(query, mydb, params=params)
            
                df = pd.to_datetime(df['Date_Listed'])
                # st.write(df[0])
                date_listed = df[0]       

                date_sold = pd.to_datetime(st.session_state.get("date_sold"))
                
                no_days = (date_sold - date_listed).days
                days_on_market = int(st.text_input("Days on Market", no_days, disabled=True))
        

            if st.button('Submit', key='submit_sales'):

                query = """
                            INSERT INTO sales (Listing_ID, Sale_Price, Date_Sold, Days_on_Market)
                            VALUES (%s, %s, %s, %s)
                        """
                val = (listing_id, sale_price, date_sold, days_on_market)
                mycursor.execute(query, val)
                mydb.commit()            
                                        
                st.success("Sales submitted successfully!")
            

        with tab5:

            st.subheader('Buyers')

            sale_id = st.selectbox("Sale ID", distinct_listing_id, index=None, placeholder="Select a Listing ID", key="listing_id_3")
            buyer_type = st.selectbox("Buyer Type", ["End User", "Investor"])
            payment_mode = st.selectbox("Payment Mode", ["Cash", "Cheque", "Bank Transfer", "UPI"])
            loan_taken = st.checkbox("Loan Taken?")
            loan_provider = st.text_input("Loan Provider")
            loan_amount = st.number_input("Loan Amount", min_value=0)       

            if st.button('Submit', key='submit_buyers'):
                query = """
                            INSERT INTO buyers (Sale_ID, Buyer_Type, Payment_Mode, Loan_Taken, Loan_Provider, Loan_Amount)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                val = (sale_id, buyer_type, payment_mode, loan_taken, loan_provider, loan_amount)
                mycursor.execute(query, val)
                mydb.commit()            
                                                                
                st.success("Sales submitted successfully!") 


# ----------------------------------------------------------
                 

    if menu == 'READ':
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Listings", "Property Attributes", "Agents", "Sales", "Buyers"])

        with tab1:
            st.subheader('Listing Data')
            
            a1, b1 = st.tabs(['All Data', 'Specific Data'])

            with a1:
                query = """
                            SELECT * 
                            FROM listing;
                        """
                df = pd.read_sql(query, mydb)

                AgGrid(
                    df,
                    pagination=True,
                    paginationPageSize=20
                )                


            with b1: 
                query = """
                    SELECT DISTINCT(Listing_ID)
                    FROM listing;
                """
                distinct_listing_id = pd.read_sql(query, mydb)
                distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()
                # st.write(len(distinct_listing_id))

                listing_id = st.multiselect("Listing ID", distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_4")
                
                if listing_id:

                    query = """
                                SELECT * 
                                FROM listing
                                where 1=1
                            """
                    
                    params = []
                    placeholder = ",".join(["%s"] * len(listing_id))
                    query += f" AND Listing_ID IN ({placeholder})"
                    params.extend(listing_id)

                    df = pd.read_sql(query, mydb, params=params)

                    st.dataframe(df)


        with tab2:
            st.subheader('Property Attributes Data')
            
            a1, b1 = st.tabs(['All Data', 'Specific Data'])

            with a1:
                query = """
                            SELECT * 
                            FROM property_attributes;
                        """
                df = pd.read_sql(query, mydb)

                AgGrid(
                    df,
                    pagination=True,
                    paginationPageSize=20
                )                


            with b1: 
                query = """
                    SELECT DISTINCT(Listing_ID)
                    FROM property_attributes;
                """
                distinct_listing_id = pd.read_sql(query, mydb)
                distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()
                # st.write(len(distinct_listing_id))

                listing_id = st.multiselect("Listing ID", distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_5")
                
                if listing_id:

                    query = """
                                SELECT * 
                                FROM property_attributes
                                where 1=1
                            """
                    
                    params = []
                    placeholder = ",".join(["%s"] * len(listing_id))
                    query += f" AND Listing_ID IN ({placeholder})"
                    params.extend(listing_id)

                    df = pd.read_sql(query, mydb, params=params)

                    st.dataframe(df)        


        with tab3:
            st.subheader('Agents Data')

            a1, b1 = st.tabs(['All Data', 'Specific Data'])

            with a1:
                query = """
                            SELECT * 
                            FROM agents;
                        """
                df = pd.read_sql(query, mydb)

                AgGrid(
                    df,
                    pagination=True,
                    paginationPageSize=20
                )                


            with b1: 
                query = """
                    SELECT DISTINCT(Agent_ID)
                    FROM listing;
                """
                distinct_agent_id = pd.read_sql(query, mydb)
                distinct_agent_id = distinct_agent_id['Agent_ID'].tolist()

                agent_id = st.multiselect("Agent ID", distinct_agent_id, placeholder="Select a Listing ID", key = 'agent_id_2')
                
                if agent_id:

                    query = """
                                SELECT * 
                                FROM agents
                                where 1=1
                            """
                    
                    params = []
                    placeholder = ",".join(["%s"] * len(agent_id))
                    query += f" AND Agent_ID IN ({placeholder})"
                    params.extend(agent_id)

                    df = pd.read_sql(query, mydb, params=params)

                    st.dataframe(df)      


        with tab4:
            st.subheader('Sales Data')
            
            a1, b1 = st.tabs(['All Data', 'Specific Data'])

            with a1:
                query = """
                            SELECT * 
                            FROM sales;
                        """
                df = pd.read_sql(query, mydb)
                st.write(df)
                # AgGrid(
                #     df,
                #     pagination=True,
                #     paginationPageSize=20
                # )                


            with b1: 
                query = """
                    SELECT DISTINCT(Listing_ID)
                    FROM sales;
                """
                distinct_listing_id = pd.read_sql(query, mydb)
                distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()
                # st.write(len(distinct_listing_id))

                listing_id = st.multiselect("Listing ID", distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_6")
                
                if listing_id:

                    query = """
                                SELECT * 
                                FROM sales
                                where 1=1
                            """
                    
                    params = []
                    placeholder = ",".join(["%s"] * len(listing_id))
                    query += f" AND Listing_ID IN ({placeholder})"
                    params.extend(listing_id)

                    df = pd.read_sql(query, mydb, params=params)

                    st.dataframe(df)        


        with tab5:
            st.subheader('Buyers Data')

            a1, b1 = st.tabs(['All Data', 'Specific Data'])

            with a1:
                query = """
                            SELECT * 
                            FROM buyers;
                        """
                df = pd.read_sql(query, mydb)

                AgGrid(
                    df,
                    pagination=True,
                    paginationPageSize=20
                )                


            with b1: 
                
                col1, col2 = st.columns(2)
                
                with col1:
                    query = """
                        SELECT DISTINCT(Sale_ID)
                        FROM buyers;
                    """
                    distinct_sale_id = pd.read_sql(query, mydb)
                    distinct_sale_id = distinct_sale_id['Sale_ID'].tolist()
                    # st.write(len(distinct_listing_id))

                    sale_id = st.multiselect("Sales ID", distinct_sale_id, placeholder="Select a Listing ID")

                    if sale_id:
                        query = """
                                    SELECT * 
                                    FROM buyers
                                    where 1=1
                                """
                        
                        params = []
                        placeholder = ",".join(["%s"] * len(sale_id))
                        query += f" AND Sale_ID IN ({placeholder})"
                        params.extend(sale_id)

                        df = pd.read_sql(query, mydb, params=params)

                        st.dataframe(df)        


                with col2:

                    query = """
                        SELECT DISTINCT(Buyer_ID)
                        FROM buyers;
                    """
                    distinct_buyer_id = pd.read_sql(query, mydb)
                    distinct_buyer_id = distinct_buyer_id['Buyer_ID'].tolist()

                    buyer_id = st.multiselect("Buyer ID", distinct_buyer_id, placeholder="Select a Listing ID")

                    if buyer_id:
                        query = """
                                    SELECT * 
                                    FROM buyers
                                    where 1=1
                                """
                        
                        params = []
                        placeholder = ",".join(["%s"] * len(buyer_id))
                        query += f" AND Buyer_ID IN ({placeholder})"
                        params.extend(buyer_id)

                        df = pd.read_sql(query, mydb, params=params)

                        st.dataframe(df)        
                                     

# ----------------------------------------------------------                                     


    if menu == 'UPDATE':
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Listings", "Property Attributes", "Agents", "Sales", "Buyers"])

        with tab1:
            st.subheader('Update Listing Data')
            query = """
                SELECT DISTINCT(Listing_ID)
                FROM listing;
            """
            distinct_listing_id = pd.read_sql(query, mydb)
            distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()

            listing_id = st.selectbox("Listing ID", ['None'] + distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_7")
            
            query = """
                        SELECT * 
                        FROM listing
                        WHERE Listing_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(listing_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if listing_id == "None":
                pass
            elif listing_id != "None":
                city = st.selectbox("City",['New York', 'Los Angeles', 'Houston', 'Phoenix', 'Chicago'], index=None, placeholder='Select City')
                property_type = st.selectbox("Property Type", ["Apartment", "Villa", "House"], index=None, placeholder='Select Property Type')
                price = st.number_input("Price", min_value=0, value=df['Price'][0])
                sqft = st.number_input("Square Feet", min_value=0, value=df["Sqft"][0])
                date_listed = st.date_input("Date Listed", value=pd.to_datetime(df['Date_Listed'][0]))
                agent_id = st.text_input("Agent ID", value=str(df['Agent_ID'][0]))
                latitude = st.number_input("Latitude", format="%.6f", value=df['Latitude'][0])
                longitude = st.number_input("Longitude", format="%.6f", value=df['Longitude'][0])

                if st.button('Update', key='update_listing'):
                    query = "UPDATE listing SET City=%s, Property_Type=%s, Price=%s, Sqft=%s, Date_Listed=%s, Agent_ID=%s, Latitude=%s, Longitude=%s WHERE Listing_ID=%s"
                    val = (city, property_type, price, sqft, date_listed, agent_id, latitude, longitude, listing_id)
                    mycursor.execute(query, val)
                    mydb.commit()
                    st.success("Listing Updated Successfully")
            
                    query = """
                                SELECT * 
                                FROM listing
                                WHERE Listing_ID = %s
                            """
                    df = pd.read_sql(query, mydb, params=(listing_id,))
                    df = pd.DataFrame(df)
                    st.write(df)


        with tab2:
            st.subheader('Update Property Attributes')
            query = """
                SELECT DISTINCT(Listing_ID)
                FROM property_attributes;
            """
            distinct_listing_id = pd.read_sql(query, mydb)
            distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()

            listing_id = st.selectbox("Listing ID", ['None'] + distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_8")
            
            query = """
                        SELECT * 
                        FROM property_attributes
                        WHERE Listing_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(listing_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if listing_id == "None":
                pass

            elif listing_id != "None":
                bedrooms = st.number_input("Bedrooms", min_value=0, max_value=8, value=df['Bedrooms'][0])
                bathrooms = st.number_input("Bathrooms", min_value=0, max_value=8, value=df['Bathrooms'][0])
                floor_number = st.number_input("Floor Number", min_value=0, value=df['Floor_Number'][0])
                total_floors = st.number_input("Total Floors", min_value=0, value=df['Total_Floors'][0])
                year_built = st.number_input("Year Built", min_value=1900, max_value=2026, value=df['Year_Built'][0])
                is_rented = int(st.checkbox("Is Rented?", value=bool(df['Is_Rented'][0])))
                tenant_count = st.number_input("Tenant Count", min_value=0, value=df['Tenant_Count'][0])
                furnishing_status = st.selectbox("Furnishing Status", ["Furnished", "Unfurnished", "Semi-Furnished"])
                metro_distance = st.number_input("Metro Distance (km)", min_value=0.0, value=df['Metro_Distance_km'][0])
                parking = int(st.checkbox("Parking Available?", value=bool(df['Parking_Available'][0])))
                power_backup = int(st.checkbox("Power Backup?", value=bool(df['Power_Backup'][0]))                )

                if st.button('Update', key='update_property_attributes'):
                    query = "UPDATE property_attributes SET Bedrooms=%s, Bathrooms=%s, Floor_Number=%s, Total_Floors=%s, Year_Built=%s, Is_Rented=%s, Tenant_Count=%s, Furnishing_Status=%s, Metro_Distance_km=%s, Parking_Available=%s, Power_Backup=%s WHERE Listing_ID=%s"
                    val = (bedrooms, bathrooms, floor_number, total_floors, year_built, is_rented, tenant_count, furnishing_status, metro_distance, parking, power_backup, listing_id)
                    mycursor.execute(query, val)
                    mydb.commit()
                    st.success("Property Attributes Updated Successfully")
            
                    query = """
                                SELECT * 
                                FROM property_attributes
                                WHERE Listing_ID = %s
                            """
                    df = pd.read_sql(query, mydb, params=(listing_id,))
                    df = pd.DataFrame(df)
                    st.write(df)                


        with tab3:
            st.subheader('Update Agents Data')
            query = """
                SELECT DISTINCT(Agent_ID)
                FROM agents;
            """
            distinct_agent_id = pd.read_sql(query, mydb)
            distinct_agent_id = distinct_agent_id['Agent_ID'].tolist()

            agent_id = st.selectbox("Agent ID", ['None'] + distinct_agent_id, placeholder="Select a Agent ID", key="agent_id_3")

            query = """
                        SELECT * 
                        FROM agents
                        WHERE Agent_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(agent_id,))
            df = pd.DataFrame(df)
            st.write(df)            

            if agent_id == "None":
                pass

            elif agent_id != "None":
                name = st.text_input("Name", value=df['Name'][0])
                phone = st.text_input("Phone", value=df['Phone'][0])
                email = st.text_input("Email", value=df['Email'][0])
                commission_rate = st.number_input("Commission Rate (%)", min_value=0, value=df['Commission_Rate'][0])
                deals_closed = st.number_input("Deals Closed", min_value=0, value=df['Deals_Closed'][0])
                rating = float(st.slider("Rating (0-5)", min_value=1.0, max_value=5.0, step=0.1, value=df['Rating'][0]))
                experience_years = st.number_input("Experience (Years)", min_value=0, value=df['Experience_Years'][0])
                avg_closing_days = st.number_input("Avg Closing Days", min_value=0, value=df['Avg_Closing_Days'][0])

                if st.button('Update', key='update_agents'):
                    query = "UPDATE agents SET Name=%s, Phone=%s, Email=%s, Commission_Rate=%s, Deals_Closed=%s, Rating=%s, Experience_Years=%s, Avg_Closing_Days=%s WHERE Agent_ID=%s"
                    val = (name, phone, email, commission_rate, deals_closed, rating, experience_years, avg_closing_days, agent_id )
                    mycursor.execute(query, val)
                    mydb.commit()
                    st.success("Agents Updated Successfully")
            
                    query = """
                                SELECT * 
                                FROM agents
                                WHERE Agent_ID = %s
                            """
                    df = pd.read_sql(query, mydb, params=(agent_id,))
                    df = pd.DataFrame(df)
                    st.write(df)                


        with tab4:
            st.subheader('Update Sales Data')
            query = """
                SELECT DISTINCT(Listing_ID)
                FROM Sales;
            """
            distinct_listing_id = pd.read_sql(query, mydb)
            distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()

            listing_id = st.selectbox("Listing ID", ['None'] + distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_9")
            
            query = """
                        SELECT * 
                        FROM Sales
                        WHERE Listing_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(listing_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if listing_id == "None":
                pass

            elif listing_id != "None":
                sale_price = st.number_input("Sale Price", min_value=0, value=df['Sale_Price'][0])
                date_sold = st.date_input("Date Sold", value=pd.to_datetime(df['Date_Sold'][0]))

                query = """
                    SELECT Date_Listed
                    FROM listing
                    WHERE Listing_ID = %s
                """
                params = []
                params = [listing_id]
                df = pd.read_sql(query, mydb, params=params)
                df = pd.to_datetime(df['Date_Listed'])
                date_listed = df[0]       

                date_sold = pd.to_datetime(date_sold)
                
                no_days = (date_sold - date_listed).days
                days_on_market = int(st.text_input("Days on Market", no_days, disabled=True))        

                if st.button('Update', key='update_agents'):
                    query = "UPDATE sales SET Sale_Price=%s, Date_Sold=%s, Days_on_Market=%s WHERE Listing_ID=%s"
                    val = (sale_price, date_sold, days_on_market, listing_id )
                    mycursor.execute(query, val)
                    mydb.commit()
                    st.success("Agents Updated Successfully")
            
                    query = """
                                SELECT * 
                                FROM sales
                                WHERE Listing_ID = %s
                            """
                    df = pd.read_sql(query, mydb, params=(listing_id,))
                    df = pd.DataFrame(df)
                    st.write(df)                


        with tab5:
            st.subheader('Update Sales Data')
            query = """
                SELECT DISTINCT(Buyer_ID)
                FROM Buyers;
            """
            distinct_buyer_id = pd.read_sql(query, mydb)
            distinct_buyer_id = distinct_buyer_id['Buyer_ID'].tolist()

            buyer_id = st.selectbox("Buyer ID", ['None'] + distinct_buyer_id, placeholder="Select a Buyer ID")
            
            query = """
                        SELECT * 
                        FROM Buyers
                        WHERE Buyer_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(buyer_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if buyer_id == "None":
                pass

            elif buyer_id != "None":
                query = """
                            SELECT Listing_ID
                            FROM listing
                        """
                df1 = pd.read_sql(query, mydb)
                df1 = pd.DataFrame(df1)      
                sales_listing_id= df1.values
                sale_id = st.selectbox("Sale ID", sales_listing_id, index=None, placeholder="Select a Sale ID")
                buyer_type = st.selectbox("Buyer Type", ["End User", "Investor"])
                payment_mode = st.selectbox("Payment Mode", ["Cash", "Cheque", "Bank Transfer", "UPI"])
                loan_taken = st.checkbox("Loan Taken?", value=df['Loan_Taken'][0])
                loan_provider = st.text_input("Loan Provider", value=df['Loan_Provider'][0])
                loan_amount = st.number_input("Loan Amount", min_value=0, value=df['Loan_Amount'][0])     

                if st.button('Update', key='update_buyers'):
                    query = "UPDATE buyers SET Sale_ID=%s, Buyer_Type=%s, Payment_Mode=%s, Loan_Taken=%s, Loan_Provider=%s, Loan_Amount=%s  WHERE Buyer_ID=%s"
                    val = (sale_id, buyer_type, payment_mode, loan_taken, loan_provider, loan_amount, buyer_id )
                    mycursor.execute(query, val)
                    mydb.commit()
                    st.success("Agents Updated Successfully")
            
                    query = """
                                SELECT * 
                                FROM buyers
                                WHERE Buyer_ID = %s
                            """
                    df = pd.read_sql(query, mydb, params=(buyer_id,))
                    df = pd.DataFrame(df)
                    st.write(df)                    


# ----------------------------------------------------------      


    if menu=='DELETE':
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Listings", "Property Attributes", "Agents", "Sales", "Buyers"])

        with tab1:
            st.subheader("Delete Listing Data")
            query = """
                SELECT DISTINCT(Listing_ID)
                FROM listing;
            """
            distinct_listing_id = pd.read_sql(query, mydb)
            distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()

            listing_id = st.selectbox("Listing ID", ['None'] + distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_10")            

            query = """
                        SELECT * 
                        FROM listing
                        WHERE Listing_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(listing_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if st.button("Delete", 'delete_listing'):
                query = """
                            DELETE FROM listing 
                            WHERE Listing_ID=%s
                        """
                mycursor.execute(query, (listing_id,))
                mydb.commit()
                st.success("Record Deleted successfully")                


        with tab2:
            st.subheader("Delete Property Attributes  Data")
            query = """
                SELECT DISTINCT(Listing_ID)
                FROM property_attributes;
            """
            distinct_listing_id = pd.read_sql(query, mydb)
            distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()

            listing_id = st.selectbox("Listing ID", ['None'] + distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_11")            

            query = """
                        SELECT * 
                        FROM property_attributes
                        WHERE Listing_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(listing_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if st.button("Delete", 'delete_property_attributes'):
                query = """
                            DELETE FROM property_attributes 
                            WHERE Listing_ID=%s
                        """
                mycursor.execute(query, (listing_id,))
                mydb.commit()
                st.success("Record Deleted successfully")                

        
        with tab3:
            st.subheader("Delete Agent Data")
            query = """
                SELECT DISTINCT(Agent_ID)
                FROM agents;
            """
            distinct_agent_id = pd.read_sql(query, mydb)
            distinct_agent_id = distinct_agent_id['Agent_ID'].tolist()

            agent_id = st.selectbox("Agent ID", ['None'] + distinct_agent_id, placeholder="Select a Listing ID", key='agent_id_4')            

            query = """
                        SELECT * 
                        FROM agents
                        WHERE Agent_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(agent_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if st.button("Delete", 'delete_agents'):
                query = """
                            DELETE FROM agents
                            WHERE Agent_ID=%s
                        """
                mycursor.execute(query, (agent_id,))
                mydb.commit()
                st.success("Record Deleted successfully")


        with tab4:
            st.subheader("Delete Sales  Data")
            query = """
                SELECT DISTINCT(Listing_ID)
                FROM sales;
            """
            distinct_listing_id = pd.read_sql(query, mydb)
            distinct_listing_id = distinct_listing_id['Listing_ID'].tolist()

            listing_id = st.selectbox("Listing ID", ['None'] + distinct_listing_id, placeholder="Select a Listing ID", key="listing_id_12")            

            query = """
                        SELECT * 
                        FROM sales
                        WHERE Listing_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(listing_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if st.button("Delete", 'delete_sales'):
                query = """
                            DELETE FROM sales 
                            WHERE Listing_ID=%s
                        """
                mycursor.execute(query, (listing_id,))
                mydb.commit()
                st.success("Record Deleted successfully")


        with tab5:
            st.subheader("Delete Buyers  Data")
            query = """
                SELECT DISTINCT(Buyer_ID)
                FROM buyers;
            """
            distinct_buyer_id = pd.read_sql(query, mydb)
            distinct_buyer_id = distinct_buyer_id['Buyer_ID'].tolist()

            buyer_id = st.selectbox("Buyer ID", ['None'] + distinct_buyer_id, placeholder="Select a Listing ID")            

            query = """
                        SELECT * 
                        FROM buyers
                        WHERE Buyer_ID = %s
                    """
            df = pd.read_sql(query, mydb, params=(buyer_id,))
            df = pd.DataFrame(df)
            st.write(df)

            if st.button("Delete", 'delete_buyers'):
                query = """
                            DELETE FROM buyers 
                            WHERE Buyer_ID=%s
                        """
                mycursor.execute(query, (buyer_id,))
                mydb.commit()
                st.success("Record Deleted successfully")   