--Basic Analytics Queries--

SELECT hotel, COUNT(*) AS total_bookings
FROM hotel_bookings
GROUP BY hotel;

SELECT arrival_date_month, COUNT(*) AS total_bookings
FROM hotel_bookings
GROUP BY arrival_date_month
ORDER BY total_bookings DESC;

SELECT SUM(revenue) AS total_revenue
FROM hotel_bookings
WHERE is_canceled = 0;

SELECT avg(total_stay) AS average_stay_length
FROM hotel_bookings;

SELECT country, COUNT(*) AS total_bookings
FROM hotel_bookings
GROUP BY country
ORDER BY total_bookings DESC
limit 10;

SELECT market_segment, COUNT(*) AS total_bookings
FROM hotel_bookings
GROUP BY market_segment
ORDER BY total_bookings DESC;

--Business Insight Queries--

SELECT ROUND(AVG(is_canceled)*100,2) AS cancellation_rate_percent
FROM hotel_bookings;

SELECT hotel, ROUND(AVG(is_canceled)*100,2) AS cancel_rate_percent
FROM hotel_bookings
GROUP BY hotel;

SELECT market_segment, ROUND(AVG(is_canceled)*100,2) AS cancel_rate_percent
FROM hotel_bookings
GROUP BY market_segment
ORDER BY cancel_rate_percent DESC;

SELECT previous_cancellations, ROUND(AVG(is_canceled)*100,2) AS current_cancel_rate
FROM hotel_bookings
GROUP BY previous_cancellations
ORDER BY previous_cancellations DESC;

SELECT previous_bookings_not_canceled, ROUND(AVG(is_canceled)*100,2) AS cancel_rate_percent
FROM hotel_bookings
GROUP BY previous_bookings_not_canceled
ORDER BY previous_bookings_not_canceled DESC;

SELECT total_of_special_requests, ROUND(AVG(is_canceled)*100,2) AS cancel_rate_percent
FROM hotel_bookings
GROUP BY total_of_special_requests
ORDER BY total_of_special_requests DESC;

SELECT CASE
         WHEN lead_time <= 7 THEN 'Last Minute (0-7 days)'
         WHEN lead_time <= 30 THEN 'Short Term (8-30 days)'
         WHEN lead_time <= 90 THEN 'Medium Term (31-90 days)'
         ELSE 'Long Term (90+ days)'
       END AS lead_time_category,
       ROUND(AVG(is_canceled)*100,2) AS cancel_rate_percent
FROM hotel_bookings
GROUP BY lead_time_category
ORDER BY cancel_rate_percent DESC;

--Customer Segmentation Queries--

--1) High-Risk Customers (For Deposit Policy)
SELECT *
FROM hotel_bookings
WHERE previous_cancellations > 1
ORDER BY previous_cancellations DESC;


--2) Loyal Customers (For Loyalty Programs)
SELECT *
FROM hotel_bookings
WHERE previous_bookings_not_canceled > 3
ORDER BY previous_bookings_not_canceled DESC;

--3) Special Requests Customers (For Personalized Services)
SELECT *
FROM hotel_bookings
WHERE total_of_special_requests >= 2
ORDER BY total_of_special_requests DESC;

--4) Last-Minute Bookers (For Targeted Marketing)
SELECT *
FROM hotel_bookings
WHERE lead_time <= 7
ORDER BY lead_time ASC;

--5) Long-Term Planners (For Early Bird Offers)
SELECT *
FROM hotel_bookings
WHERE lead_time >= 90
ORDER BY lead_time DESC;