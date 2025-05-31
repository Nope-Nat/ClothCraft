COPY "user" (id_user, username, email, password_hash, admin) FROM stdin;
e5e4c4ab-069f-40eb-8e85-1bc523672b18	johnsmith	johnsmith@example.com	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa	False
6f404e00-7ab5-41fd-af04-dd52e2c2d72e	janedoe	janedoe@example.com	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa	False
db8565da-240c-4c5f-adfd-d6dac2fadd04	alexbrown	alexbrown@example.com	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa	True
cc98b556-fc0a-40b6-826c-3ffdbd87d4c4	emilyc	emilyc@example.com	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa	False
bd4b8db9-5f54-4bca-9ffa-91b68405cdd2	aliceh	aliceh@example.com	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa	False
\.

COPY session (id_session, id_user, ip, device_details, logged_at) FROM stdin;
1	e5e4c4ab-069f-40eb-8e85-1bc523672b18	192.168.1.10	Chrome 120.0 Windows 10	2024-06-01 09:01:00
2	6f404e00-7ab5-41fd-af04-dd52e2c2d72e	192.168.1.11	Firefox 116.0 Linux	2024-06-01 10:02:00
3	db8565da-240c-4c5f-adfd-d6dac2fadd04	192.168.1.13	Safari 13.1 Mac	2024-06-02 12:30:00
4	cc98b556-fc0a-40b6-826c-3ffdbd87d4c4	192.168.1.12	Edge Win	2024-06-03 14:00:00
\.

COPY country (id_country, name, short_code) FROM stdin;
1	Poland	POL
2	Germany	DEU
3	Italy	ITA
4	France	FRA
5	Spain	ESP
\.

COPY category (id_category, parent_category, name, created_at) FROM stdin;
1	\N	Tops	2024-06-01 00:00:00
2	\N	Bottoms	2024-06-01 00:00:00
3	\N	Outerwear	2024-06-01 00:00:00
4	1	T-shirts	2024-06-01 00:10:00
5	1	Shirts	2024-06-01 00:20:00
6	2	Jeans	2024-06-01 00:30:00
7	2	Shorts	2024-06-01 00:40:00
8	3	Jackets	2024-06-01 00:50:00
\.

COPY sizing_type (id_sizing_type, name, created_at) FROM stdin;
1	Men International	2024-06-01 00:00:00
2	Women International	2024-06-01 00:00:00
3	Unisex International	2024-06-01 00:00:00
\.

COPY sizing_format (id_sizing_format, value, created_at) FROM stdin;
1	S	2024-06-01 00:00:00
2	M	2024-06-01 00:01:00
3	L	2024-06-01 00:02:00
4	XL	2024-06-01 00:03:00
5	XS	2024-06-01 00:04:00
6	XXL	2024-06-01 00:05:00
\.

COPY size (id_size, id_sizing_type, "order", created_at) FROM stdin;
1	1	1	2024-06-01 00:00:00
2	1	2	2024-06-01 00:01:00
3	1	3	2024-06-01 00:02:00
4	1	4	2024-06-01 00:03:00
5	1	5	2024-06-01 00:04:00
6	2	1	2024-06-01 00:10:00
7	2	2	2024-06-01 00:11:00
8	2	3	2024-06-01 00:12:00
9	2	4	2024-06-01 00:13:00
10	2	5	2024-06-01 00:14:00
\.

COPY size_data (id_size, id_sizing_format, value, created_at) FROM stdin;
1	1	S	2024-06-01 00:00:00
2	2	M	2024-06-01 00:01:00
3	3	L	2024-06-01 00:02:00
4	4	XL	2024-06-01 00:03:00
5	5	XS	2024-06-01 00:04:00
6	1	S	2024-06-01 00:10:00
7	2	M	2024-06-01 00:11:00
8	3	L	2024-06-01 00:12:00
9	4	XL	2024-06-01 00:13:00
10	5	XS	2024-06-01 00:14:00
\.

COPY material_type (id_material_type, name, description, recyclable, weight_per_unit) FROM stdin;
1	Cotton	Cotton fabric	True	0.8
2	Polyester	Synthetic polyester yarn	False	0.7
3	Denim	Denim cotton	True	0.9
4	Viscose	Soft viscose fibers	False	0.75
5	Elastane	Stretch fiber	False	0.6
\.

COPY material (id_material, id_material_type, origin) FROM stdin;
1	1	1
2	2	2
3	3	3
4	4	4
5	5	5
6	1	2
\.

COPY product (id_product, id_category, id_sizing_type, id_country, sku_code, active, short_description, thumbnail_path, name, created_at) FROM stdin;
1	4	1	1	TSHIRT001	True	Cotton basic t-shirt	/static/img/example1.webp	Basic T-shirt	2024-06-02 08:00:00
2	5	1	2	SHIRT001	True	Casual shirt with long sleeves	/static/img/example2.webp	Casual Shirt	2024-06-02 08:01:00
3	6	1	3	JEANS001	True	Straight fit blue jeans	/static/img/example3.webp	Blue Jeans	2024-06-02 08:05:00
4	7	1	1	SHORTS001	True	Cotton shorts	/static/img/example4.webp	Cotton Shorts	2024-06-02 08:10:00
5	8	1	2	JACKET001	True	Denim jacket	/static/img/example5.webp	Denim Jacket	2024-06-02 08:12:00
6	4	1	3	TSHIRT002	True	White t-shirt with logo	/static/img/example6.webp	Logo T-shirt	2024-06-02 08:15:00
7	5	1	4	SHIRT002	True	Slim fit shirt blue	/static/img/example7.webp	Slim Blue Shirt	2024-06-02 08:18:00
8	4	1	5	TSHIRT003	True	Black T-shirt	/static/img/example8.webp	Black T-shirt	2024-06-02 08:20:00
9	7	1	1	SHORTS002	True	Denim shorts	/static/img/example9.webp	Denim Shorts	2024-06-02 08:25:00
10	6	1	2	JEANS002	True	Skinny jeans	/static/img/example10.webp	Skinny Jeans	2024-06-02 08:30:00
\.

COPY product_details_history (id_product, description, created_at) FROM stdin;
1	Basic cotton t-shirt for casual wear.	2024-06-02 08:01:00
2	Casual long-sleeve shirt, suitable for everyday use.	2024-06-02 08:02:00
3	Straight fit blue jeans made from high quality cotton.	2024-06-02 08:06:00
4	Comfortable cotton shorts for summer.	2024-06-02 08:11:00
5	Classic denim jacket.	2024-06-02 08:13:00
6	White t-shirt with printed logo.	2024-06-02 08:16:00
7	Slim fit shirt in blue color.	2024-06-02 08:19:00
8	Black casual t-shirt.	2024-06-02 08:21:00
9	Denim shorts for kids.	2024-06-02 08:26:00
10	Skinny jeans modern look.	2024-06-02 08:31:00
\.

COPY product_image (id_product, img_path, "order", alt_desc) FROM stdin;
1	/img/tshirts/basic.jpg	1	Basic T-shirt front
2	/img/shirts/casual_long.jpg	1	Casual Shirt
3	/img/jeans/straightfit.jpg	1	Blue Jeans
4	/img/shorts/cotton.jpg	1	Cotton Shorts
5	/img/jackets/denim.jpg	1	Denim Jacket
6	/img/tshirts/logo_white.jpg	1	Logo T-shirt
7	/img/shirts/slim_blue.jpg	1	Slim Blue Shirt
8	/img/tshirts/black.jpg	1	Black T-shirt
9	/img/shorts/denim.jpg	1	Denim Shorts
10	/img/jeans/skinny.jpg	1	Skinny Jeans
\.

COPY discount_history (id_product, discount, "from", "to", secret_code) FROM stdin;
2	10.0	2024-06-10 10:00:00	2024-06-15 10:00:00	SUMMER10
4	5.0	2024-06-12 09:00:00	2024-06-20 14:00:00	JUNE4
9	8.0	2024-06-20 09:00:00	2024-06-21 10:00:00	KIDD8
\.

COPY price_history (id_product, price, created_at) FROM stdin;
1	25.99	2024-06-02 08:00:00
2	39.90	2024-06-02 08:01:00
3	55.99	2024-06-02 08:05:00
4	19.99	2024-06-02 08:10:00
5	65.00	2024-06-02 08:12:00
6	29.99	2024-06-02 08:15:00
7	44.99	2024-06-02 08:18:00
8	24.99	2024-06-02 08:20:00
9	22.50	2024-06-02 08:25:00
10	59.90	2024-06-02 08:30:00
\.

COPY variant (id_variant, id_product, name, color, active, created_at) FROM stdin;
1	1	Red	RED	True	2024-06-02 09:00:00
2	1	Black	BLK	True	2024-06-02 09:01:00
3	2	Blue	BLU	True	2024-06-02 09:02:00
4	2	White	WHT	True	2024-06-02 09:03:00
5	3	Denim	BLU	True	2024-06-02 09:04:00
6	3	Black	BLK	True	2024-06-02 09:05:00
7	4	Grey	GRY	True	2024-06-02 09:06:00
8	5	Denim	BLU	True	2024-06-02 09:07:00
9	6	White	WHT	True	2024-06-02 09:08:00
10	7	Blue	BLU	True	2024-06-02 09:09:00
\.

COPY variant_size (id_variant_size, id_variant, id_size, created_at) FROM stdin;
1	1	1	2024-06-02 10:00:00
2	1	2	2024-06-02 10:01:00
3	2	1	2024-06-02 10:03:00
4	2	2	2024-06-02 10:04:00
5	3	2	2024-06-02 10:05:00
6	3	3	2024-06-02 10:06:00
7	4	2	2024-06-02 10:07:00
8	5	3	2024-06-02 10:08:00
9	6	4	2024-06-02 10:09:00
10	7	2	2024-06-02 10:10:00
11	7	3	2024-06-02 10:11:00
12	8	2	2024-06-02 10:12:00
13	9	1	2024-06-02 10:13:00
14	9	3	2024-06-02 10:14:00
15	10	1	2024-06-02 10:15:00
\.

COPY tag (id_tag, name, created_at) FROM stdin;
1	summer	2024-06-01 00:00:00
2	new	2024-06-01 01:00:00
3	bestseller	2024-06-01 02:00:00
4	denim	2024-06-01 03:00:00
5	cotton	2024-06-01 04:00:00
\.

COPY tag_product (id_tag, id_product) FROM stdin;
1	1
2	1
5	1
1	2
2	2
3	3
4	3
5	4
1	4
3	5
4	5
2	6
3	7
1	8
4	9
5	10
\.

COPY storage_delivery (id_storage_delivery, delivered_at) FROM stdin;
1	2024-06-01 09:00:00
2	2024-06-05 14:00:00
3	2024-06-10 13:00:00
\.

COPY storage_delivery_part (id_delivery, id_variant_size, quantity) FROM stdin;
1	1	100
1	2	100
1	3	100
1	4	100
2	5	80
2	6	80
2	7	80
3	8	50
3	9	45
3	10	50
3	11	40
3	12	60
2	13	70
2	14	75
1	15	60
\.

COPY product_material (id_product, id_material, percentage, created_at) FROM stdin;
1	1	100.0	2024-06-02 08:00:00
2	1	80.0	2024-06-02 08:01:00
2	2	20.0	2024-06-02 08:01:00
3	3	99.0	2024-06-02 08:05:00
3	5	1.0	2024-06-02 08:05:00
4	1	80.0	2024-06-02 08:10:00
4	5	20.0	2024-06-02 08:10:00
5	3	95.0	2024-06-02 08:12:00
5	2	5.0	2024-06-02 08:12:00
6	6	100.0	2024-06-02 08:15:00
7	2	100.0	2024-06-02 08:18:00
8	2	80.0	2024-06-02 08:20:00
8	5	20.0	2024-06-02 08:20:00
9	3	98.0	2024-06-02 08:25:00
9	5	2.0	2024-06-02 08:25:00
10	1	70.0	2024-06-02 08:30:00
10	5	30.0	2024-06-02 08:30:00
\.

COPY "order" (id_order, shipping_price, id_user, payed_at, cancelled_at, shippment_tracking_number, return_tracking_number, secret_code) FROM stdin;
1	10.0	e5e4c4ab-069f-40eb-8e85-1bc523672b18	2024-06-10 09:00:00	\N	11111111-1111-1111-1111-111111111111	\N	ORDERSC1
2	12.5	6f404e00-7ab5-41fd-af04-dd52e2c2d72e	2024-06-10 10:00:00	\N	22222222-2222-2222-2222-222222222222	\N	ORDERSC2
3	8.0	cc98b556-fc0a-40b6-826c-3ffdbd87d4c4	2024-06-11 14:00:00	2024-06-13 16:00:00	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444444	ORDERSC3
4	9.0	db8565da-240c-4c5f-adfd-d6dac2fadd04	2024-06-16 15:00:00	\N	55555555-5555-5555-5555-555555555555	\N	ORDERSC4
\.

COPY order_history (id_order, status, created_at) FROM stdin;
1	paid	2024-06-10 09:05:00
1	shipped	2024-06-11 09:00:00
1	delivered	2024-06-13 10:00:00
2	paid	2024-06-10 10:01:00
2	shipped	2024-06-12 08:00:00
3	paid	2024-06-11 14:05:00
3	cancelled	2024-06-13 16:10:00
4	paid	2024-06-16 15:10:00
4	shipped	2024-06-17 09:00:00
\.

COPY order_product (id_order, id_variant_size, quantity) FROM stdin;
1	1	1
1	3	2
2	5	1
2	8	3
2	9	1
3	6	2
3	7	1
4	10	2
4	14	1
\.

COPY cart_product_variant (id_user, id_variant_size, quantity) FROM stdin;
e5e4c4ab-069f-40eb-8e85-1bc523672b18	1	2
e5e4c4ab-069f-40eb-8e85-1bc523672b18	2	1
6f404e00-7ab5-41fd-af04-dd52e2c2d72e	3	2
db8565da-240c-4c5f-adfd-d6dac2fadd04	5	1
db8565da-240c-4c5f-adfd-d6dac2fadd04	8	3
cc98b556-fc0a-40b6-826c-3ffdbd87d4c4	9	1
bd4b8db9-5f54-4bca-9ffa-91b68405cdd2	11	2
bd4b8db9-5f54-4bca-9ffa-91b68405cdd2	12	1
\.


