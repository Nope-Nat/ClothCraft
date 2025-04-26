-- sizing_type
COPY sizing_type (name) FROM stdin;
T-Shirts
Shoes
Pants
\.

-- sizing_format
COPY sizing_format (value) FROM stdin;
US
UK
EU
\.

-- category
COPY category (parent_category, name) FROM stdin;
\N	Tops
\N	Bottoms
\N	Footwear
1	Graphic Tees
2	Denim Jeans
3	Canvas Sneakers
\.

-- size
COPY size (id_sizing_type, "order") FROM stdin;
1	1
1	2
1	3
1	4
2	1
2	2
2	3
3	1
3	2
3	3
\.

-- size_data
COPY size_data (id_size, id_sizing_format, value) FROM stdin;
1	1	S
1	2	S
1	3	S
2	1	M
2	2	M
2	3	M
3	1	L
3	2	L
3	3	L
4	1	XL
4	2	XL
4	3	XL
5	1	7
5	2	7
5	3	40
6	1	8
6	2	8
6	3	41
7	1	9
7	2	9
7	3	42
8	1	30
8	2	30
8	3	46
9	1	32
9	2	32
9	3	48
10	1	34
10	2	34
10	3	50
\.

-- product
COPY product (id_category, id_sizing_type, sku_code, published, short_description, thumbnail_path, name) FROM stdin;
4	1	CCTSH001	true	"A classic crew-neck tee, breathable cotton."	NULL	Crafted Crew Neck Tee
5	3	CCDJP001	true	"Premium straight-fit denim jeans."	NULL	Artisan Denim Jeans
6	2	CCSNK001	true	"Lightweight canvas sneakers, handwoven finish."	NULL	Handwoven Canvas Sneakers
\.

-- product_details
COPY product_details (id_product, description) FROM stdin;
1	"# Crafted Crew Neck Tee\n\n- 100% organic cotton\n- Available in multiple colors\n- Machine wash cold"
2	"# Artisan Denim Jeans\n\n- 98% cotton, 2% elastane\n- Stone-washed finish\n- Slim straight cut"
3	"# Handwoven Canvas Sneakers\n\n- Breathable canvas upper\n- Rubber sole\n- Ethically handcrafted"
\.

-- variant
COPY variant (id_product, name, color) FROM stdin;
1	Crafted Crew Neck Tee – White	#FFFFFF
1	Crafted Crew Neck Tee – Black	#000000
2	Artisan Denim Jeans – Indigo	#4B0082
2	Artisan Denim Jeans – Stone Grey	#A9A9A9
3	Handwoven Canvas Sneakers – Offwhite	#F5F5DC
3	Handwoven Canvas Sneakers – Onyx	#353839
\.

-- variant_size
COPY variant_size (id_variant_size, id_variant, id_size, quantity) FROM stdin;
1	1	1	10
2	1	2	10
3	1	3	10
4	1	4	10
5	2	1	8
6	2	2	8
7	2	3	8
8	2	4	8
9	3	8	5
10	3	9	5
11	3	10	5
12	4	8	6
13	4	9	6
14	4	10	6
15	5	5	7
16	5	6	7
17	5	7	7
18	6	5	4
19	6	6	4
20	6	7	4
\.

-- discount_history
COPY discount_history (id_product, discount, "from", "to") FROM stdin;
2	15.0	2025-01-01 00:00:00	\N
3	10.0	2025-02-01 00:00:00	2025-03-01 00:00:00
\.

-- price_history
COPY price_history (id_product, price) FROM stdin;
1	19.99
2	49.99
3	59.99
\.

-- tag
COPY tag (name) FROM stdin;
casual
denim
sustainable
artisan
\.

-- tag_product
COPY tag_product (id_tag, id_product) FROM stdin;
1	1
3	1
2	2
4	2
1	3
4	3
\.
