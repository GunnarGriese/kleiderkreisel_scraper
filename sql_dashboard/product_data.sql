SELECT
    date,
    product_name,
    CAST(price AS INT64) AS price,
    IF(
        REGEXP_CONTAINS(img_link, r ','),
        REGEXP_EXTRACT(img_link, r '(.*?),.*'),
        img_link
    ) AS img_link,
    brand,
    color,
    condition,
    PARSE_DATE('%Y-%m-%d', release_date) AS release_date
FROM
    (
        SELECT
            date,
            product_name,
            brand,
            condition,
            color,
            REGEXP_EXTRACT(release_datetime, r '(.*?)T.*') AS release_date,
            REGEXP_EXTRACT(price, r '(.*?),.*') price,
            REGEXP_EXTRACT(pic_links, r '\[(.*?)\]') AS img_link
        FROM
            `kleiderkreisel-scraper.gunnar.minimum_shirt`
    )