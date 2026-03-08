show databases;

use project_1;

show tables;

-- Property & Pricing Analysis

-- 1) Average listing price by city

SELECT * FROM listing;

SELECT City, Avg(Price)
FROM listing
GROUP BY City;

-- 2) Average price per square foot by property type

SELECT Property_Type, ROUND(AVG(Price/Sqft)) AS avg_price_per_square_foot
FROM listing
GROUP BY Property_Type;

-- 3) Furnishing status impact property prices

SELECT * FROM property_attributes;

SELECT pa.Furnishing_Status, AVG(l.Price)
FROM listing l
INNER JOIN property_attributes pa
ON l.Listing_Id = pa.Listing_ID
GROUP BY pa.Furnishing_Status
ORDER BY avg_price DESC;

-- 4) Propertiex closer to metro stations command higher prices

SELECT MIN(Metro_Distance_km) as min, MAX(Metro_Distance_km) as max
FROM property_attributes;

SELECT 
	CASE
		WHEN pa.Metro_Distance_km BETWEEN 0 AND 3 THEN '<3 KM'
        WHEN pa.Metro_Distance_km BETWEEN 3.1 AND 5 THEN '3 - 5 KM'
        WHEN pa.Metro_Distance_km BETWEEN 5.1 AND 10 THEN '5 - 10 KM'
        WHEN pa.Metro_Distance_km BETWEEN 10.1 AND 15  THEN '10 - 15 KM'
	END AS distance,
    ROUND(AVG(l.Price)) AS avg_price
FROM listing l
INNER JOIN property_attributes pa
	ON l.Listing_ID = pa.Listing_ID
GROUP BY distance
ORDER BY avg_price DESC;


-- 5) Rented properties priced differently from non-rented ones

SELECT 
	CASE
		WHEN pa.Is_Rented = 0 THEN 'Not Rented'
        WHEN pa.Is_Rented = 1 THEN 'Rented'
    END AS rented_status,
	ROUND(AVG(Price)) AS avg_price
FROM listing l
INNER JOIN property_attributes pa
	 On l.Listing_ID = pa.Listing_ID
GROUP BY rented_status
ORDER BY avg_Price;
    
    
-- 6) bedrooms and bathrooms affect pricing

SELECT pa.Bedrooms, pa.Bathrooms, ROUND(AVG(l.Price)) AS avg_price
FROM listing l
INNER JOIN property_attributes pa
	on l.Listing_ID = pa.Listing_ID
GROUP BY pa.Bedrooms, pa.Bathrooms
ORDER BY pa.Bedrooms;


-- 7) properties with parking and power backup sell at higher prices

SELECT 
	CASE
		WHEN pa.Parking_Available = 0 THEN 'No Parking'
        WHEN pa.Parking_Available = 1 THEN 'Parking'
	END AS parking,
    CASE
		WHEN pa.Power_Backup = 0 THEN 'No Power Backup'
        WHEN pa.Power_Backup = 1 THEN 'Power Backup'
	END AS power_backup,
    ROUND(AVG(l.Price)) AS avg_price
FROM listing l
INNER JOIN property_attributes pa
	ON l.Listing_ID = pa.Listing_ID
GROUP BY parking, power_backup
ORDER BY avg_price;


-- 8) year built influence listing price

SELECT pa.Year_Built, ROUND(AVG(l.Price)) AS avg_price
FROM listing l
INNER JOIN property_attributes pa
	ON l.Listing_ID = pa.Listing_ID
GROUP BY pa.Year_Built
ORDER BY pa.Year_Built;


-- 9) cities have the highest median property prices

-- step 1	
SELECT 
	City,
	Price,
	ROW_NUMBER() OVER(PARTITION BY City ORDER BY Price) AS rn,
	COUNT(*) OVER(PARTITION BY City) AS cnt
FROM listing;


-- step 2

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
    ROUND(AVG(Price)) as median
FROM ordered_price
WHERE rn IN (FLOOR((cnt+1)/2), FLOOR((cnt+2) /2))
GROUP BY City;


-- 10) How are properties distributed across price buckets



-- 11. average days on markey by city

select * from sales;

SELECT l.City, ROUND(Avg(s.Days_on_Market)) AS avg_days_on_market
FROM listing l
INNER JOIN sales s
	ON l.Listing_ID = s.Listing_ID
GROUP BY l.City
ORDER BY avg_days_on_market;


-- 12. property types sell the fastest

SELECT l.Property_Type, ROUND(AVG(s.Days_on_Market)) AS avg_days_on_market
FROM listing l
INNER JOIN sales s
	ON l.Listing_ID = s.Listing_ID
GROUP BY l.Property_Type
ORDER BY avg_days_on_market;


-- 13. Percentage of properties are sold above listing price

select * from sales;

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


-- 14. sale-to-list price ration by city


-- 15.listings took more than 90 days to sell

SELECT 
	l.Listing_ID,
    s.Days_on_Market
FROM listing l
INNER JOIN sales s
	ON l.Listing_ID = s.Listing_ID
WHERE s.Days_on_Market > 90
ORDER BY s.Days_on_Market DESC;


-- 16. Metro distance affect time on market

select * from property_attributes;

DESC property_attributes;


SELECT 
	CASE 
		WHEN pa.Metro_Distance_km BETWEEN 0 AND 1 THEN '<=1 km'
        WHEN pa.Metro_Distance_Km BETWEEN 1 AND 3 THEN '1-3 km'
        WHEN pa.Metro_Distance_Km BETWEEN 3 AND 5 THEN '3-5 km'
        WHEN pa.Metro_Distance_Km BETWEEN 5 AND 10 THEN '5-10 km'
        WHEN pa.Metro_Distance_Km BETWEEN 10 AND 15 THEN '10 -15 km'
        ELSE '>15 km'
	END AS distance,
    ROUND(AVG(s.Days_on_Market)) AS avg_days
FROM property_attributes pa
INNER JOIN sales s
	ON pa.Listing_ID = s.Listing_ID
GROUP BY distance
ORDER BY distance;


-- 17. monthly sales trend

SELECT
	DATE_FORMAT(Date_Sold, '%Y-%m') AS sales_month,
    ROUND(AVG(Sale_Price)) AS avg_sales,
    COUNT(*) AS sales_count
FROM sales
GROUP BY sales_month
ORDER BY sales_month;


-- 18. properties are currently unsold

SELECT
	l.Property_Type,
    COUNT(*) AS unsold
FROM listing l
LEFT JOIN sales s
	ON l.Listing_ID = s.Listing_ID
WHERE s.Listing_ID IS NULL
GROUP BY l.Property_Type
ORDER BY unsold;
    

-- Agent Performance

-- 19. Agents have closed the most sales

SELECT * FROM agents;

SELECT Agent_ID, Name, Deals_Closed 
FROM agents
ORDER BY Deals_Closed DESC LIMIT 1;


-- 20. Top agents by total sales revenue

SELECT * FROM sales;

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
    DENSE_RANK() OVER(ORDER BY total_sales_revenue DESC) AS Ranking
FROM agent_revenue
)
SELECT * 
FROM ranked_agents
WHERE Ranking <= 5;
		
        
-- 21. agents close deals fastest

SELECT Agent_ID, Name, Avg_Closing_Days
FROM agents
ORDER BY Avg_Closing_Days LIMIT 5;


-- 22.Experience correlate with deals closed

/* 
correlation = cov(x, y) / (var(x) var(y))
cov(x, y) = Σ(x-x̄)(y-ȳ)/N
var(x) = Σ(x-x̄)^2 /N

correlation other formula
*/

SELECT * FROM agents;

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
    ) AS pearson_correlation
FROM agents;


-- 23. Agents with higher ratings cLOse deals faster

select* from agents;


SELECT 
	CASE
		WHEN Rating >=1 AND Rating <=2 THEN '1-2'
        WHEN Rating > 2 AND Rating <=3 THEN '2-3'
        WHEN Rating > 3 AND Rating <= 4 THEN '3 - 4'
        WHEN Rating > 3.5 AND Rating <= 4 THEN '3.5 - 4'
        WHEN Rating > 4 AND Rating <= 4.5 THEN '4 -4.5'
        WHEN Rating > 4.5 AND Rating <= 5 THEN '4.5 - 5'
	END AS rating_range,
	AVG(Avg_Closing_Days)
FROM agents
GROUP BY rating_range
ORDER BY rating_range DESC;


-- 24. average commision earned by each agent

SELECT 
	a.Agent_ID,
    ROUND((s.Sale_Price * a.Commission_Rate) / 100) AS Commission_price
FROM agents a
INNER JOIN listing l
	ON a.Agent_ID = l.Agent_ID
INNER JOIN sales s
	ON l.Listing_ID = s.Listing_ID;


-- 25. Agents currently have the most active listings (unsold)

SELECT 
	a.Agent_ID,
    a.Name,
    COUNT(l.Listing_ID) AS active_listings
FROM agents a
INNER JOIN listing l
	ON a.Agent_ID = l.Agent_ID
LEFT JOIN sales s
	ON l.Listing_ID = s.Listing_ID
WHERE s.Listing_ID IS NULL
GROUP BY a.Agent_ID
ORDER BY active_listings DESC LIMIT 10;



-- Buyer & Financing Behavior

-- 26. Percentage of buyers are investors vs end users

select * from buyers;

SELECT 
    Buyer_Type,
    COUNT(*) AS Count,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS Percentage
FROM buyers
GROUP BY Buyer_Type;


-- 27. cities have the highest loan uptake rate

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


-- 28. Average loan amount by buyer type

SELECT 
	Buyer_Type,
    AVG(Loan_Amount) AS Avg_Loan_Amount
FROM Buyers
GROUP BY Buyer_Type;


-- 29. Payment mode is most commonly used

SELECT
	Payment_Mode,
    COUNT(Payment_Mode) AS Payment_Method
FROM buyers
GROUP BY Payment_Mode
ORDER BY Payment_Method DESC;


-- 30. loan-backed purchases take longer to close

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
    