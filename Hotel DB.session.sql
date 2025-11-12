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



