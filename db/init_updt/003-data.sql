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
4	1	1	TSHIRT001	True	Cotton basic t-shirt	/static/img/example1.webp	Basic T-shirt	2024-06-02 18:00:00
5	1	2	SHIRT001	True	Casual shirt with long sleeves	/static/img/example2.webp	Casual Shirt	2024-06-02 18:01:00
6	2	3	JEANS001	True	Straight fit blue jeans	/static/img/example3.webp	Blue Jeans	2024-06-02 18:05:00
7	1	1	SHORTS001	True	Cotton shorts	/static/img/example4.webp	Cotton Shorts	2024-06-02 18:10:00
8	5	2	JACKET001	True	Denim jacket	/static/img/example5.webp	Denim Jacket	2024-06-02 18:12:00
4	1	3	TSHIRT002	True	White t-shirt with logo	/static/img/example6.webp	Logo T-shirt	2024-06-02 18:15:00
5	1	4	SHIRT002	True	Slim fit shirt blue	/static/img/example7.webp	Slim Blue Shirt	2024-06-02 18:18:00
4	1	5	TSHIRT003	True	Black T-shirt	/static/img/example8.webp	Black T-shirt	2024-06-02 18:20:00
7	4	1	SHORTS002	True	Kids denim shorts	/static/img/example9.webp	Kids Denim Shorts	2024-06-02 18:25:00
6	2	2	JEANS002	True	Skinny jeans	/static/img/example10.webp	Skinny Jeans	2024-06-02 18:30:00
4	1	1	TSHIRT004	True	V-neck cotton t-shirt	/static/img/no_image.png	V-Neck T-shirt	2024-06-02 08:35:00
4	1	2	TSHIRT005	True	Striped pattern t-shirt	/static/img/no_image.png	Striped T-shirt	2024-06-02 08:40:00
5	1	3	SHIRT003	True	Classic flannel shirt	/static/img/no_image.png	Flannel Shirt	2024-06-02 08:45:00
5	1	4	SHIRT004	True	Oxford button-down shirt	/static/img/no_image.png	Oxford Shirt	2024-06-02 08:50:00
6	2	5	PANTS001	True	Chino pants beige	/static/img/no_image.png	Chinos	2024-06-02 08:55:00
7	1	1	SHORTS003	True	Cargo shorts with pockets	/static/img/no_image.png	Cargo Shorts	2024-06-02 09:00:00
8	5	2	JACKET002	True	Bomber jacket lightweight	/static/img/no_image.png	Bomber Jacket	2024-06-02 09:05:00
8	1	3	HOODIE001	True	Cotton pullover hoodie	/static/img/no_image.png	Hoodie	2024-06-02 09:10:00
8	5	4	BLAZER001	True	Business casual blazer	/static/img/no_image.png	Blazer	2024-06-02 09:15:00
8	1	5	CARDIGAN01	True	Knit cardigan sweater	/static/img/no_image.png	Cardigan	2024-06-02 09:20:00
4	4	1	KIDSTSH001	True	Kids colorful t-shirt	/static/img/no_image.png	Kids T-shirt	2024-06-02 09:25:00
8	4	2	KIDSHOD001	True	Kids hooded sweatshirt	/static/img/no_image.png	Kids Hoodie	2024-06-02 09:30:00
6	4	3	KIDSJNS001	True	Kids stretch jeans	/static/img/no_image.png	Kids Jeans	2024-06-02 09:35:00
1	4	4	KIDSDRS001	True	Kids summer dress	/static/img/no_image.png	Kids Dress	2024-06-02 09:40:00
4	1	5	SPORTTSH01	True	Athletic performance t-shirt	/static/img/no_image.png	Sports T-shirt	2024-06-02 09:45:00
\.

-- Keep the rest of the data as is since they reference generated IDs or are composite keys
COPY product_details_history (id_product, description, created_at) FROM stdin;
1	# Basic Cotton T-Shirt\n\n## Product Overview\nThis **premium cotton t-shirt** is perfect for everyday casual wear. Made from 100% organic cotton, it offers exceptional comfort and breathability.\n\n## Features\n* **Material**: 100% organic cotton\n* **Fit**: Classic regular fit\n* **Weight**: 180 GSM fabric\n* **Care**: Machine washable at 30°C\n\n## Sizing\nThis t-shirt follows standard men's sizing. For the best fit:\n* **S**: Chest 36-38 inches\n* **M**: Chest 38-40 inches\n* **L**: Chest 40-42 inches\n\n## Sustainability\n✅ Made from *organic cotton*\n✅ **Eco-friendly** production process\n✅ Fair trade certified\n\n**Perfect for**: Casual outings, gym sessions, layering	2024-06-02 08:01:00
2	# Casual Long-Sleeve Shirt\n\n## Premium Comfort for Every Occasion\n\nThis **versatile long-sleeve shirt** combines style and comfort, making it ideal for both work and leisure activities.\n\n## Key Features\n* **Fabric Blend**: 80% cotton, 20% polyester\n* **Style**: Button-down collar with chest pocket\n* **Fit**: Relaxed comfortable fit\n* **Wrinkle Resistance**: Easy-care fabric\n\n## Design Details\n- Classic button-down design\n- *Adjustable cuffs* for perfect fit\n- **Chest pocket** for small essentials\n- Curved hem for versatile styling\n\n## Care Instructions\n1. Machine wash cold (30°C)\n2. Tumble dry low heat\n3. Iron on medium heat if needed\n\n> *"The perfect shirt for transitioning from office to weekend"*\n\n**Styling Tips**: Pair with jeans for casual look or chinos for smart-casual	2024-06-02 08:02:00
3	# Straight Fit Blue Jeans\n\n## Classic Denim Excellence\n\nThese **premium straight-fit jeans** are crafted from high-quality cotton denim, offering the perfect balance of comfort and durability.\n\n## Technical Specifications\n* **Denim Weight**: 12 oz premium cotton\n* **Fit**: Straight leg with mid-rise waist\n* **Construction**: 5-pocket classic design\n* **Hardware**: YKK zipper, riveted stress points\n\n## Features & Benefits\n### Comfort\n- **99% cotton, 1% elastane** for slight stretch\n- Pre-washed for *softness*\n- **Reinforced seams** for durability\n\n### Style\n- Classic **indigo blue** wash\n- Authentic fading patterns\n- Versatile straight-leg silhouette\n\n## Size Guide\n| Size | Waist | Inseam | Rise |\n|------|-------|--------| ---- |\n| 30   | 30"   | 32"    | 10"  |\n| 32   | 32"   | 32"    | 10"  |\n| 34   | 34"   | 32"    | 10.5"|\n\n**Perfect for**: Everyday wear, casual Fridays, weekend adventures	2024-06-02 08:06:00
4	# Cotton Summer Shorts\n\n## Beat the Heat in Style\n\nThese **lightweight cotton shorts** are your go-to choice for hot summer days, combining comfort with contemporary style.\n\n## Summer-Ready Features\n* **Breathable Cotton**: 80% cotton, 20% elastane blend\n* **Length**: 7-inch inseam for optimal comfort\n* **Pockets**: 4-pocket design including coin pocket\n* **Waistband**: Elastic waistband with drawstring\n\n## Comfort Technology\n- **Moisture-wicking** properties\n- *Quick-dry* fabric treatment\n- **UPF 30+** sun protection\n- Flat-seam construction prevents chafing\n\n## Activity Ready\n✅ **Beach days** - sand-resistant fabric\n✅ **Gym workouts** - flexible stretch fabric\n✅ **Casual outings** - stylish contemporary fit\n✅ **Travel** - wrinkle-resistant material\n\n## Care & Maintenance\n- Machine wash cold\n- Hang dry recommended\n- No bleach or fabric softener\n\n> *Designed for the active lifestyle*\n\n**Color Options**: Available in multiple summer-ready colors	2024-06-02 08:11:00
5	# Classic Denim Jacket\n\n## Timeless Style Meets Modern Comfort\n\nThis **iconic denim jacket** is a wardrobe essential that never goes out of style. Crafted from premium denim with attention to every detail.\n\n## Premium Construction\n* **Material**: 95% cotton denim, 5% polyester blend\n* **Weight**: Heavy-duty 13 oz denim\n* **Hardware**: Antique brass buttons and rivets\n* **Lining**: Soft cotton twill lining\n\n## Design Heritage\n### Classic Elements\n- **Traditional western styling**\n- Pointed flap chest pockets\n- *Adjustable side tabs* at waist\n- **Vintage-inspired** wash treatment\n\n### Modern Updates\n- Improved fit through shoulders\n- **Reinforced stress points**\n- Pre-shrunk fabric\n- Enhanced range of motion\n\n## Versatile Styling\n| Season | Styling Suggestion |\n|--------|-------------------|\n| Spring | Over light sweaters |\n| Summer | With t-shirts and shorts |\n| Fall   | **Layering piece** with hoodies |\n| Winter | Under heavy coats |\n\n## Care Instructions\n⚠️ **First Wash**: Wash separately to prevent color transfer\n- Cold water wash (30°C)\n- Turn inside out\n- Hang dry to maintain shape\n\n**Investment Piece**: Built to last for years with proper care	2024-06-02 08:13:00
6	# Logo T-Shirt - Premium White\n\n## Brand Statement Piece\n\nThis **premium white t-shirt** features our signature logo print, combining brand recognition with superior comfort and quality.\n\n## Premium Materials\n* **Fabric**: 100% Pima cotton (single jersey knit)\n* **Weight**: 200 GSM for durability\n* **Print**: High-quality **screen print** logo\n* **Neckline**: Reinforced crew neck\n\n## Logo Design\n- **Placement**: Center chest positioning\n- **Size**: Proportioned for optimal visibility\n- **Technique**: *Fade-resistant* screen printing\n- **Colors**: Multi-color logo design\n\n## Quality Features\n### Construction\n- **Double-needle** hem stitching\n- Pre-shrunk fabric\n- *Shoulder-to-shoulder* tape reinforcement\n- Tag-free comfort printing\n\n### Comfort\n- **Soft-hand feel** Pima cotton\n- Breathable single jersey knit\n- Classic fit that's not too tight or loose\n\n## Brand Heritage\n> *"Wear your values with pride"*\n\nThis logo represents our commitment to:\n- ♻️ **Sustainable practices**\n- 👥 Fair trade manufacturing\n- 🌱 **Organic materials**\n- 💪 Quality craftsmanship\n\n## Care Guide\n1. Machine wash cold with like colors\n2. **Do not bleach** to preserve logo\n3. Tumble dry low\n4. Iron on reverse side if needed\n\n**Statement Piece**: Perfect for brand enthusiasts and everyday wear	2024-06-02 08:16:00
7	# Slim Blue Shirt - Modern Fit\n\n## Contemporary Professional Style\n\nThis **modern slim-fit shirt** in classic blue is designed for the contemporary professional who values both style and comfort.\n\n## Tailored Excellence\n* **Fit**: Slim cut through body with tapered waist\n* **Fabric**: 100% premium cotton poplin\n* **Collar**: Semi-spread collar, stays included\n* **Cuffs**: Barrel cuffs with single button\n\n## Professional Features\n### Business Ready\n- **Wrinkle-resistant** finish\n- *Easy-iron* cotton treatment\n- **Non-transparent** fabric weight\n- Chest pocket with pen slot\n\n### Comfort Technology\n- **Stretch-enhanced** for mobility\n- Moisture-wicking properties\n- *Breathable* cotton weave\n- **Comfortable** all-day wear\n\n## Styling Versatility\n\n**Office Wear**:\n- With suit and tie for formal meetings\n- Business casual with chinos\n\n**Smart Casual**:\n- Open collar with dark jeans\n- *Layered under* sweaters or cardigans\n\n## Size & Fit Guide\n- **Chest**: Measured under arms across fullest part\n- **Neck**: Measured around base of neck\n- **Sleeve**: From shoulder seam to wrist\n\n| Size | Chest | Neck | Sleeve |\n|------|-------|------|--------|\n| S    | 38"   | 15"  | 33"    |\n| M    | 40"   | 15.5"| 34"    |\n| L    | 42"   | 16"  | 35"    |\n\n## Fabric Care\n- Professional dry cleaning recommended\n- Or machine wash cold, hang dry\n- Iron while slightly damp for best results\n\n**Professional Essential**: A must-have for the modern wardrobe	2024-06-02 08:19:00
8	# Black Casual T-Shirt\n\n## Versatile Wardrobe Essential\n\nThis **premium black t-shirt** is the ultimate versatile piece - perfect for layering, standalone wear, or as a foundation for any casual outfit.\n\n## Premium Black Fabric\n* **Material**: 80% cotton, 20% elastane blend\n* **Color**: Deep black with **fade-resistant** dye\n* **Weight**: 180 GSM medium weight\n* **Finish**: Pre-shrunk and enzyme washed\n\n## Superior Comfort\n### Fit & Feel\n- **Soft-touch** cotton blend\n- Slight stretch for *comfort*\n- **Breathable** fabric construction\n- Classic crew neck design\n\n### Quality Construction\n- **Reinforced** shoulder seams\n- Double-stitched hem\n- *Tear-away* label for comfort\n- **Color-matched** stitching\n\n## Versatility Champion\n\n**Layering Options**:\n- Under jackets and cardigans\n- With **open shirts** for dimension\n- Base layer for *athletic wear*\n\n**Standalone Styling**:\n- With jeans for classic casual\n- **Dressed up** with blazer\n- Gym and workout sessions\n\n## Color Psychology\n> *Black is the ultimate neutral - it goes with everything*\n\n**Benefits of Black**:\n- ✅ **Slimming** effect\n- ✅ Hides stains better\n- ✅ *Professional* appearance\n- ✅ **Timeless** appeal\n\n## Fabric Technology\n- **Moisture management** for active wear\n- Anti-microbial treatment\n- *Shape retention* after washing\n- **Pilling-resistant** surface\n\n## Care Instructions\n⚠️ **Preserve the black**: Always wash in cold water\n- Turn inside out before washing\n- Use color-protecting detergent\n- Avoid bleach or harsh chemicals\n- Air dry when possible\n\n**Wardrobe Staple**: The foundation piece every closet needs	2024-06-02 08:21:00
9	# Kids Denim Shorts\n\n## Adventure-Ready for Little Explorers\n\nThese **durable kids' denim shorts** are designed to keep up with active children while providing comfort and style for summer adventures.\n\n## Kid-Friendly Design\n* **Material**: 98% cotton denim, 2% elastane\n* **Construction**: Reinforced knees and seat\n* **Safety**: All edges finished, no sharp hardware\n* **Comfort**: Soft internal seams\n\n## Active Kids Features\n### Durability\n- **Triple-stitched** stress points\n- *Reinforced pockets* for treasures\n- **Tear-resistant** premium denim\n- Secure button and zipper\n\n### Comfort & Safety\n- **Adjustable waistband** with internal elastic\n- Soft cotton lining at waistband\n- *Rounded pocket corners*\n- **Easy-reach** pocket design\n\n## Size Range & Growth\n\n**Available Sizes**: 4-14 years\n\n| Age | Size | Waist | Length |\n|-----|------|-------|--------|\n| 4-5 | XS   | 20"   | 11"    |\n| 6-7 | S    | 22"   | 12"    |\n| 8-9 | M    | 24"   | 13"    |\n| 10-11| L   | 26"   | 14"    |\n| 12-14| XL  | 28"   | 15"    |\n\n## Parent-Approved Features\n✅ **Easy care** - machine washable\n✅ *Stain-resistant* treatment\n✅ **Quick-dry** for active play\n✅ Fade-resistant color\n✅ **Grow-with-me** adjustable waist\n\n## Activity Ready\n- **Playground adventures**\n- Beach and water play\n- *Camping and hiking*\n- **School and casual wear**\n- Sports activities\n\n## Care Instructions\n👶 **Kid-safe cleaning**:\n- Machine wash warm (40°C)\n- Use gentle, **kid-friendly** detergent\n- Tumble dry medium\n- *Pre-treat stains* with gentle stain remover\n\n## Educational Fun\n> *Teaching kids about quality and durability*\n\n**Life Lessons**:\n- **Taking care** of belongings\n- Quality vs. quantity choices\n- *Sustainable* fashion habits\n\n**Growing Up**: Designed to last through growth spurts and adventures	2024-06-02 08:26:00
10	# Skinny Jeans - Modern Silhouette\n\n## Contemporary Fit Revolution\n\nThese **modern skinny jeans** offer a sleek, contemporary silhouette while maintaining the comfort and quality you expect from premium denim.\n\n## Advanced Denim Technology\n* **Fabric Blend**: 70% cotton, 30% elastane\n* **Stretch**: 4-way stretch technology\n* **Recovery**: Shape-retention fibers\n* **Weight**: 11 oz lightweight denim\n\n## Skinny Fit Engineering\n### Tailored Precision\n- **Slim through hip and thigh**\n- Tapered leg from knee to ankle\n- *Mid-rise waistline* for comfort\n- **Contoured waistband** prevents gapping\n\n### Comfort Innovation\n- **360-degree stretch** for mobility\n- Recovery technology maintains shape\n- *Soft-hand feel* with stretch\n- **All-day comfort** guarantee\n\n## Modern Wash Treatment\n\n**Contemporary Finish**:\n- Subtle fading for *authentic look*\n- **Whiskering** at natural stress points\n- Clean hem finish\n- *Minimal distressing* for versatility\n\n## Styling Guide\n\n**Casual Styling**:\n- With sneakers and t-shirts\n- **Rolled cuffs** with ankle boots\n- Oversized sweaters for balance\n\n**Dressed Up**:\n- *Blazer and dress shoes*\n- **Button-down shirts** tucked in\n- Heeled boots for elongated silhouette\n\n## Fit Technology\n\n**Size Optimization**:\n- **True to size** with stretch accommodation\n- Inseam options: 30", 32", 34"\n- *Rise options*: Mid-rise standard\n\n## Sustainability Focus\n♻️ **Eco-Conscious Production**:\n- Water-saving wash processes\n- **Recycled** hardware components\n- *Sustainable* cotton sourcing\n- Reduced chemical usage\n\n## Care for Longevity\n**Maintaining Skinny Fit**:\n1. **Wash inside out** in cold water\n2. Hang dry to maintain stretch\n3. *Avoid harsh detergents*\n4. **Steam** instead of ironing when possible\n\n## Performance Metrics\n- **Stretch Recovery**: 95% after 8 hours\n- Color Fastness: *Excellent* rating\n- **Durability**: 200+ wash cycles tested\n- Comfort Rating: **5/5** customer satisfaction\n\n**Modern Essential**: Where style meets performance in contemporary denim	2024-06-02 08:31:00
11	V-neck cotton t-shirt with modern fit.	2024-06-02 08:36:00
12	Striped pattern t-shirt for casual style.	2024-06-02 08:41:00
13	Classic flannel shirt perfect for autumn.	2024-06-02 08:46:00
14	Oxford button-down shirt for business casual.	2024-06-02 08:51:00
15	Chino pants in beige color for versatile styling.	2024-06-02 08:56:00
16	Cargo shorts with multiple pockets for utility.	2024-06-02 09:01:00
17	Lightweight bomber jacket for transitional weather.	2024-06-02 09:06:00
18	Cotton pullover hoodie for comfort and warmth.	2024-06-02 09:11:00
19	Business casual blazer for professional settings.	2024-06-02 09:16:00
20	Knit cardigan sweater perfect for layering.	2024-06-02 09:21:00
21	Colorful t-shirt designed specifically for children.	2024-06-02 09:26:00
22	Kids hooded sweatshirt for playground activities.	2024-06-02 09:31:00
23	Stretch jeans for kids with adjustable waist.	2024-06-02 09:36:00
24	Summer dress for girls with floral pattern.	2024-06-02 09:41:00
25	Athletic performance t-shirt with moisture-wicking technology.	2024-06-02 09:46:00
\.

COPY product_image (id_product, img_path, "order", alt_desc) FROM stdin;
1	/static/img/example1.webp	1	Basic T-shirt front
2	/static/img/example2.webp	1	Casual Shirt
3	/static/img/example3.webp	1	Blue Jeans
4	/static/img/example4.webp	1	Cotton Shorts
5	/static/img/example5.webp	1	Denim Jacket
6	/static/img/example6.webp	1	Logo T-shirt
7	/static/img/example7.webp	1	Slim Blue Shirt
8	/static/img/example8.webp	1	Black T-shirt
9	/static/img/example9.webp	1	Denim Shorts
10	/static/img/example10.webp	1	Skinny Jeans
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
11	27.99	2024-06-02 08:35:00
12	32.50	2024-06-02 08:40:00
13	49.99	2024-06-02 08:45:00
14	52.00	2024-06-02 08:50:00
15	48.99	2024-06-02 08:55:00
16	24.99	2024-06-02 09:00:00
17	79.99	2024-06-02 09:05:00
18	45.00	2024-06-02 09:10:00
19	89.99	2024-06-02 09:15:00
20	55.50	2024-06-02 09:20:00
21	18.99	2024-06-02 09:25:00
22	35.00	2024-06-02 09:30:00
23	39.99	2024-06-02 09:35:00
24	28.50	2024-06-02 09:40:00
25	34.99	2024-06-02 09:45:00
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
11	Navy	NVY	True	2024-06-02 09:10:00
11	White	WHT	True	2024-06-02 09:11:00
12	Red	RED	True	2024-06-02 09:12:00
12	Navy	NVY	True	2024-06-02 09:13:00
13	Red	RED	True	2024-06-02 09:14:00
13	Blue	BLU	True	2024-06-02 09:15:00
14	White	WHT	True	2024-06-02 09:16:00
14	Blue	BLU	True	2024-06-02 09:17:00
15	Beige	BGE	True	2024-06-02 09:18:00
15	Navy	NVY	True	2024-06-02 09:19:00
16	Khaki	KHK	True	2024-06-02 09:20:00
17	Black	BLK	True	2024-06-02 09:21:00
17	Navy	NVY	True	2024-06-02 09:22:00
18	Grey	GRY	True	2024-06-02 09:23:00
18	Black	BLK	True	2024-06-02 09:24:00
19	Navy	NVY	True	2024-06-02 09:25:00
19	Grey	GRY	True	2024-06-02 09:26:00
20	Grey	GRY	True	2024-06-02 09:27:00
20	Navy	NVY	True	2024-06-02 09:28:00
21	Blue	BLU	True	2024-06-02 09:29:00
21	Red	RED	True	2024-06-02 09:30:00
22	Grey	GRY	True	2024-06-02 09:31:00
22	Blue	BLU	True	2024-06-02 09:32:00
23	Blue	BLU	True	2024-06-02 09:33:00
23	Black	BLK	True	2024-06-02 09:34:00
24	Pink	PNK	True	2024-06-02 09:35:00
24	Blue	BLU	True	2024-06-02 09:36:00
25	Black	BLK	True	2024-06-02 09:37:00
25	White	WHT	True	2024-06-02 09:38:00
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
11	2	2024-06-02 10:26:00
11	3	2024-06-02 10:27:00
11	4	2024-06-02 10:28:00
12	1	2024-06-02 10:29:00
12	2	2024-06-02 10:30:00
12	3	2024-06-02 10:31:00
13	2	2024-06-02 10:32:00
13	3	2024-06-02 10:33:00
13	4	2024-06-02 10:34:00
14	3	2024-06-02 10:35:00
14	4	2024-06-02 10:36:00
15	2	2024-06-02 10:37:00
15	3	2024-06-02 10:38:00
15	4	2024-06-02 10:39:00
16	7	2024-06-02 10:40:00
16	8	2024-06-02 10:41:00
16	9	2024-06-02 10:42:00
17	8	2024-06-02 10:43:00
17	9	2024-06-02 10:44:00
18	2	2024-06-02 10:45:00
18	3	2024-06-02 10:46:00
18	4	2024-06-02 10:47:00
19	19	2024-06-02 10:48:00
19	20	2024-06-02 10:49:00
19	21	2024-06-02 10:50:00
20	2	2024-06-02 10:51:00
20	3	2024-06-02 10:52:00
20	4	2024-06-02 10:53:00
21	19	2024-06-02 10:54:00
21	20	2024-06-02 10:55:00
21	21	2024-06-02 10:56:00
22	15	2024-06-02 10:57:00
22	16	2024-06-02 10:58:00
22	17	2024-06-02 10:59:00
23	19	2024-06-02 11:00:00
23	20	2024-06-02 11:01:00
23	21	2024-06-02 11:02:00
24	15	2024-06-02 11:03:00
24	16	2024-06-02 11:04:00
24	17	2024-06-02 11:05:00
25	15	2024-06-02 11:06:00
25	16	2024-06-02 11:07:00
25	17	2024-06-02 11:08:00
26	2	2024-06-02 11:09:00
26	3	2024-06-02 11:10:00
26	4	2024-06-02 11:11:00
27	3	2024-06-02 11:12:00
27	4	2024-06-02 11:13:00
28	1	2024-06-02 11:14:00
28	2	2024-06-02 11:15:00
28	3	2024-06-02 11:16:00
\.

-- Add more tags for better categorization
COPY tag (name, created_at) FROM stdin;
summer	2024-06-01 00:00:00
new	2024-06-01 01:00:00
bestseller	2024-06-01 02:00:00
denim	2024-06-01 03:00:00
cotton	2024-06-01 04:00:00
casual	2024-06-01 05:00:00
formal	2024-06-01 06:00:00
kids	2024-06-01 07:00:00
sports	2024-06-01 08:00:00
vintage	2024-06-01 09:00:00
eco-friendly	2024-06-01 10:00:00
winter	2024-06-01 11:00:00
\.

-- Tag more products to ensure good distribution
COPY tag_product (id_tag, id_product) FROM stdin;
1	1
2	1
5	1
6	1
1	2
2	2
6	2
3	3
4	3
5	4
1	4
6	4
3	5
4	5
2	6
6	6
3	7
6	7
1	8
6	8
4	9
8	9
5	10
6	10
2	11
5	11
6	11
2	12
5	12
6	12
10	13
5	13
6	13
7	14
5	14
6	15
5	15
1	16
6	16
12	17
2	17
12	18
5	18
7	19
2	19
12	20
5	20
8	21
2	21
8	22
2	22
8	23
4	23
8	24
2	24
9	25
2	25
11	25
\.

-- Add more storage deliveries for better inventory distribution
COPY storage_delivery (delivered_at) FROM stdin;
2024-06-01 09:00:00
2024-06-05 14:00:00
2024-06-10 13:00:00
2024-06-15 10:00:00
2024-06-20 12:00:00
2024-06-25 11:00:00
2024-06-30 15:00:00
\.

-- Add storage delivery parts for all new variant sizes
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
4	16	90
4	17	85
4	18	95
4	19	70
4	20	75
4	21	80
5	22	60
5	23	65
5	24	70
5	25	50
5	26	55
5	27	60
6	28	40
6	29	45
6	30	50
6	31	35
6	32	40
6	33	45
7	34	25
7	35	30
7	36	35
7	37	20
7	38	25
7	39	30
7	40	15
7	41	20
7	42	25
7	43	18
7	44	22
7	45	20
7	46	12
7	47	15
7	48	18
3	49	30
3	50	35
3	51	40
4	52	25
4	53	30
4	54	35
5	55	20
5	56	25
5	57	30
6	58	15
6	59	18
6	60	22
7	61	10
7	62	12
7	63	15
7	64	8
7	65	10
7	66	12
7	67	25
7	68	30
7	69	35
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

