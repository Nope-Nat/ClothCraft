COPY "user" (id_user, username, email, password_hash, admin) FROM stdin;
e5e4c4ab-069f-40eb-8e85-1bc523672b18	johnsmith	johnsmith@example.com	ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f	False
6f404e00-7ab5-41fd-af04-dd52e2c2d72e	janedoe	janedoe@example.com	ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f	False
db8565da-240c-4c5f-adfd-d6dac2fadd04	alexbrown	alexbrown@example.com	ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f	True
cc98b556-fc0a-40b6-826c-3ffdbd87d4c4	emilyc	emilyc@example.com	ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f	False
bd4b8db9-5f54-4bca-9ffa-91b68405cdd2	aliceh	aliceh@example.com	ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f	False
\.

-- Remove id_session from COPY - let SERIAL auto-generate
COPY session (id_user, ip, device_details, logged_at) FROM stdin;
e5e4c4ab-069f-40eb-8e85-1bc523672b18	192.168.1.10	Chrome 120.0 Windows 10	2024-06-01 09:01:00
6f404e00-7ab5-41fd-af04-dd52e2c2d72e	192.168.1.11	Firefox 116.0 Linux	2024-06-01 10:02:00
db8565da-240c-4c5f-adfd-d6dac2fadd04	192.168.1.13	Safari 13.1 Mac	2024-06-02 12:30:00
cc98b556-fc0a-40b6-826c-3ffdbd87d4c4	192.168.1.12	Edge Win	2024-06-03 14:00:00
\.

-- Remove id_country from COPY - let SERIAL auto-generate
COPY country (name, short_code) FROM stdin;
Poland	POL
Germany	DEU
Italy	ITA
France	FRA
Spain	ESP
\.

-- Remove id_category from COPY - let SERIAL auto-generate
COPY category (parent_category, name, created_at) FROM stdin;
\N	Tops	2024-06-01 00:00:00
\N	Bottoms	2024-06-01 00:00:00
\N	Outerwear	2024-06-01 00:00:00
1	T-shirts	2024-06-01 00:10:00
1	Shirts	2024-06-01 00:20:00
2	Jeans	2024-06-01 00:30:00
2	Shorts	2024-06-01 00:40:00
3	Jackets	2024-06-01 00:50:00
\.

-- Remove id_sizing_type from COPY - let SERIAL auto-generate
COPY sizing_type (name, created_at) FROM stdin;
T-shirt Sizing	2024-06-01 00:00:00
Jeans Sizing	2024-06-01 00:01:00
Shoe Sizing	2024-06-01 00:02:00
Kids Clothing	2024-06-01 00:03:00
Jacket Sizing	2024-06-01 00:04:00
\.

-- Remove id_sizing_format from COPY - let SERIAL auto-generate
COPY sizing_format (value, created_at) FROM stdin;
US	2024-06-01 00:00:00
EU	2024-06-01 00:01:00
UK	2024-06-01 00:02:00
International	2024-06-01 00:03:00
\.

-- Remove id_size from COPY - Create proper size combinations for each sizing type
COPY size (id_sizing_type, "order", created_at) FROM stdin;
1	1	2024-06-01 00:00:00
1	2	2024-06-01 00:01:00
1	3	2024-06-01 00:02:00
1	4	2024-06-01 00:03:00
1	5	2024-06-01 00:04:00
2	1	2024-06-01 00:10:00
2	2	2024-06-01 00:11:00
2	3	2024-06-01 00:12:00
2	4	2024-06-01 00:13:00
2	5	2024-06-01 00:14:00
3	1	2024-06-01 00:20:00
3	2	2024-06-01 00:21:00
3	3	2024-06-01 00:22:00
3	4	2024-06-01 00:23:00
4	1	2024-06-01 00:30:00
4	2	2024-06-01 00:31:00
4	3	2024-06-01 00:32:00
4	4	2024-06-01 00:33:00
5	1	2024-06-01 00:40:00
5	2	2024-06-01 00:41:00
5	3	2024-06-01 00:42:00
5	4	2024-06-01 00:43:00
\.

-- Create proper size_data with different formats for each sizing type
COPY size_data (id_size, id_sizing_format, value, created_at) FROM stdin;
1	4	XS	2024-06-01 00:00:00
1	1	XS	2024-06-01 00:00:01
2	4	S	2024-06-01 00:01:00
2	1	S	2024-06-01 00:01:01
3	4	M	2024-06-01 00:02:00
3	1	M	2024-06-01 00:02:01
4	4	L	2024-06-01 00:03:00
4	1	L	2024-06-01 00:03:01
5	4	XL	2024-06-01 00:04:00
5	1	XL	2024-06-01 00:04:01
6	1	28	2024-06-01 00:10:00
6	2	30	2024-06-01 00:10:01
7	1	30	2024-06-01 00:11:00
7	2	32	2024-06-01 00:11:01
8	1	32	2024-06-01 00:12:00
8	2	34	2024-06-01 00:12:01
9	1	34	2024-06-01 00:13:00
9	2	36	2024-06-01 00:13:01
10	1	36	2024-06-01 00:14:00
10	2	38	2024-06-01 00:14:01
11	1	7	2024-06-01 00:20:00
11	2	40	2024-06-01 00:20:01
11	3	6	2024-06-01 00:20:02
12	1	8	2024-06-01 00:21:00
12	2	42	2024-06-01 00:21:01
12	3	7	2024-06-01 00:21:02
13	1	9	2024-06-01 00:22:00
13	2	43	2024-06-01 00:22:01
13	3	8	2024-06-01 00:22:02
14	1	10	2024-06-01 00:23:00
14	2	44	2024-06-01 00:23:01
14	3	9	2024-06-01 00:23:02
15	4	2-3Y	2024-06-01 00:30:00
16	4	4-5Y	2024-06-01 00:31:00
17	4	6-7Y	2024-06-01 00:32:00
18	4	8-9Y	2024-06-01 00:33:00
19	4	XS	2024-06-01 00:40:00
19	1	XS	2024-06-01 00:40:01
20	4	S	2024-06-01 00:41:00
20	1	S	2024-06-01 00:41:01
21	4	M	2024-06-01 00:42:00
21	1	M	2024-06-01 00:42:01
22	4	L	2024-06-01 00:43:00
22	1	L	2024-06-01 00:43:01
\.

-- Remove id_material_type from COPY - let SERIAL auto-generate
COPY material_type (name, description, recyclable, weight_per_unit) FROM stdin;
Cotton	Cotton fabric	True	0.8
Polyester	Synthetic polyester yarn	False	0.7
Denim	Denim cotton	True	0.9
Viscose	Soft viscose fibers	False	0.75
Elastane	Stretch fiber	False	0.6
\.

-- Remove id_material from COPY - let SERIAL auto-generate  
COPY material (id_material_type, origin) FROM stdin;
1	1
2	2
3	3
4	4
5	5
1	2
\.

-- Remove id_product from COPY - let SERIAL auto-generate
COPY product (id_category, id_sizing_type, id_country, sku_code, active, short_description, thumbnail_path, name, created_at) FROM stdin;
4	1	1	TSHIRT001	True	Cotton basic t-shirt	/static/img/example1.webp	Basic T-shirt	2024-06-02 08:00:00
5	1	2	SHIRT001	True	Casual shirt with long sleeves	/static/img/example2.webp	Casual Shirt	2024-06-02 08:01:00
6	2	3	JEANS001	True	Straight fit blue jeans	/static/img/example3.webp	Blue Jeans	2024-06-02 08:05:00
7	1	1	SHORTS001	True	Cotton shorts	/static/img/example4.webp	Cotton Shorts	2024-06-02 08:10:00
8	5	2	JACKET001	True	Denim jacket	/static/img/example5.webp	Denim Jacket	2024-06-02 08:12:00
4	1	3	TSHIRT002	True	White t-shirt with logo	/static/img/example6.webp	Logo T-shirt	2024-06-02 08:15:00
5	1	4	SHIRT002	True	Slim fit shirt blue	/static/img/example7.webp	Slim Blue Shirt	2024-06-02 08:18:00
4	1	5	TSHIRT003	True	Black T-shirt	/static/img/example8.webp	Black T-shirt	2024-06-02 08:20:00
7	4	1	SHORTS002	True	Kids denim shorts	/static/img/example9.webp	Kids Denim Shorts	2024-06-02 08:25:00
6	2	2	JEANS002	True	Skinny jeans	/static/img/example10.webp	Skinny Jeans	2024-06-02 08:30:00
\.

-- Keep the rest of the data as is since they reference generated IDs or are composite keys
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

-- Remove id_variant from COPY - let SERIAL auto-generate
COPY variant (id_product, name, color, active, created_at) FROM stdin;
1	Red	RED	True	2024-06-02 09:00:00
1	Black	BLK	True	2024-06-02 09:01:00
2	Blue	BLU	True	2024-06-02 09:02:00
2	White	WHT	True	2024-06-02 09:03:00
3	Denim	BLU	True	2024-06-02 09:04:00
3	Black	BLK	True	2024-06-02 09:05:00
4	Grey	GRY	True	2024-06-02 09:06:00
5	Denim	BLU	True	2024-06-02 09:07:00
6	White	WHT	True	2024-06-02 09:08:00
7	Blue	BLU	True	2024-06-02 09:09:00
\.

-- Remove id_variant_size from COPY and create proper variant sizes matching the sizing types
COPY variant_size (id_variant, id_size, created_at) FROM stdin;
1	2	2024-06-02 10:00:00
1	3	2024-06-02 10:01:00
1	4	2024-06-02 10:02:00
2	2	2024-06-02 10:03:00
2	3	2024-06-02 10:04:00
2	4	2024-06-02 10:05:00
3	2	2024-06-02 10:06:00
3	3	2024-06-02 10:07:00
3	4	2024-06-02 10:08:00
4	3	2024-06-02 10:09:00
4	4	2024-06-02 10:10:00
5	7	2024-06-02 10:11:00
5	8	2024-06-02 10:12:00
5	9	2024-06-02 10:13:00
6	8	2024-06-02 10:14:00
6	9	2024-06-02 10:15:00
7	2	2024-06-02 10:16:00
7	3	2024-06-02 10:17:00
8	19	2024-06-02 10:18:00
8	20	2024-06-02 10:19:00
8	21	2024-06-02 10:20:00
9	2	2024-06-02 10:21:00
9	3	2024-06-02 10:22:00
9	4	2024-06-02 10:23:00
10	16	2024-06-02 10:24:00
10	17	2024-06-02 10:25:00
\.

-- Remove id_tag from COPY - let SERIAL auto-generate
COPY tag (name, created_at) FROM stdin;
summer	2024-06-01 00:00:00
new	2024-06-01 01:00:00
bestseller	2024-06-01 02:00:00
denim	2024-06-01 03:00:00
cotton	2024-06-01 04:00:00
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

-- Remove id_storage_delivery from COPY - let SERIAL auto-generate
COPY storage_delivery (delivered_at) FROM stdin;
2024-06-01 09:00:00
2024-06-05 14:00:00
2024-06-10 13:00:00
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

COPY product_material (id_product, id_material, percentage) FROM stdin;
1	1	100.0
2	1	80.0
2	2	20.0
3	3	99.0
3	5	1.0
4	1	80.0
4	5	20.0
5	3	95.0
5	2	5.0
6	6	100.0
7	2	100.0
8	2	80.0
8	5	20.0
9	3	98.0
9	5	2.0
10	1	70.0
10	5	30.0
\.

-- Remove id_order from COPY - let SERIAL auto-generate
COPY "order" (shipping_price, id_user, payed_at, cancelled_at, shippment_tracking_number, return_tracking_number, secret_code) FROM stdin;
10.0	e5e4c4ab-069f-40eb-8e85-1bc523672b18	2024-06-10 09:00:00	\N	11111111-1111-1111-1111-111111111111	\N	ORDERSC1
12.5	6f404e00-7ab5-41fd-af04-dd52e2c2d72e	2024-06-10 10:00:00	\N	22222222-2222-2222-2222-222222222222	\N	ORDERSC2
8.0	cc98b556-fc0a-40b6-826c-3ffdbd87d4c4	2024-06-11 14:00:00	2024-06-13 16:00:00	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444444	ORDERSC3
9.0	db8565da-240c-4c5f-adfd-d6dac2fadd04	2024-06-16 15:00:00	\N	55555555-5555-5555-5555-555555555555	\N	ORDERSC4
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


