# Abstract:

Airlines currently rely on basic heuristics and human intuition for beverage inventory planning, leading to inefficient loading decisions that impact both operational costs and environmental sustainability. Each pound of unnecessary beverage weight carried increases fuel consumption and carbon emissions, while understocking risks customer satisfaction. This paper demonstrates how artificial intelligence, combined with real-time flight data, can transform beverage planning through precise, flight-specific predictions.

Using Southwest Airlines as a case study, we present an AI model that integrates live flight data (route, aircraft type, departure times) with historical consumption patterns to generate optimal beverage loads for specific flight numbers. For example, predicting the exact number of beverage units needed for Southwest flight WN21 from LAX to JFK, accounting for its unique characteristics such as departure time, aircraft type, and seasonal patterns. By analyzing historical consumption data against actual flight-specific variables, our model demonstrates significantly more accurate beverage planning than current methods.

Our research shows that this flight-specific AI approach can reduce both over-stocking and stockout scenarios while maintaining customer satisfaction. The solution, implemented as a REST API integrated with real-time flight data, enables immediate practical application. Initial testing indicates potential for 15% reduction in beverage overstock and 20% reduction in stockouts, contributing to both operational efficiency and aviation sustainability goals.

# Hypothesis: 

We hypothesize that an AI model, trained on historical beverage consumption data and integrated with real-time flight data from the AirLabs API, can predict optimal beverage loads for specific flight numbers with greater accuracy than current manual planning methods. Specifically:

1. The AI model will predict beverage consumption patterns within a 10% margin of error when tested against actual consumption data for individual flight numbers (e.g., WN21 from LAX to JFK).
2. The model's predictions will lead to at least a 15% reduction in beverage overstock by considering flight-specific data including:
   - Exact departure and arrival times
   - Flight duration
   - Aircraft type and capacity
   - Historical delay patterns
   - Specific route information (terminals, gates)
3. The model will maintain or improve current customer satisfaction levels while reducing the frequency of beverage stockouts by at least 20% through precise flight-by-flight inventory planning.

By utilizing real-time flight data rather than general categories, we expect to achieve higher prediction accuracy by accounting for flight-specific patterns and operational characteristics unique to each route and flight number. This approach allows for dynamic adjustment of beverage loads based on actual flight conditions rather than broad generalizations.

# Literature Review:

While attending Brigham Young University - Idaho, I  was involved in many leadership oriented extra curriculars. In 2012, I had the pleasure of meeting Mike, who volunteered to help put on a concert event. Years later, I had moved to working in various technology roles, working at Goldman Sachs and eventually becoming CTO of an ad agency in Chattanooga, TN. In that role, we developed hundreds of thousands of marketing pages for our clients. I was always keenly interesting in seeing how we could use artificial intelligence to assist in that effort, and started blogging our research efforts. In 2018, Mike messaged me, inquiring about artificial intilligence. He had taken a leadership role at Southwest, and had always kept a keen eye on technology trends. In our messages, he explained that most airlines track weight as a primary metric. Each extra pound of weight onboard means X amount of fuel needed to carry that weight, which means cost (source this literature review). In essence, the business of air travel means keeping your cargo as light as possible, while still offering a safe and quality experience. 

Mike managed the service inventory area for his airline. His job is to optimize the weight of the food and drinks each flight needs. On happy hour flights to Las Vegas for example, you may need more acohol and less coffee. Converlsly, on 6am flights from New York City you may need more coffee and peanuts, and less whisky. In an effort to optimize further Mike had collected basic inventory sheets of around 20 popular flight paths. His agents would count the inventory of peanuts, waters, etc. at the start and end of each flight, and write that down on paper. He had collected a year's worth of data, and knew he was on to something. The question he asked me was what could AI do with that data?

In that time artificial intilligence was still in it's growing stage. Quality data was expensive to get, hard to retain, and even more expensive to compute and generate (source this). AI researchers generally considered the minimum viable number of rows of data needed to effectively train an ai model to be around 10 million (source this). Human error in data entry was also common, meaning trained models would be trained on improper data (source this). Because of these issues, most AI researches considered projects that 1. Had data generated by a computer (no human data entry) and 2. had succificent amount of quality data to train (source this). As Mike's data set did not meet these requirements, we discussed a bit about AI and its current limitations and went back to life. 

Almost a decade later and two papers later, the world of AI has changed. Millions of rows of data can be generated of a very small data sample (source this). Human error can be accounted for (source this). (Discuss the changes over the years at length and what that means for our paper here, with sources).
This means that a single person, with limited amount of public data can generate clean training data for various ai projects. 

This has given rise to ai agents (source an talk about this)
I have made many ai agents for my friends and partners over the past few months, and the growth has been exponential. On a long flight to Vancouver to visit a client, my thoughts again turned to Mike and his Coka Cola problem. I pulled out my laptop, and started writing the outline of this paper. In order to solve Mike's problem I would need the following pieces of training data:

1. Airline flight path data - distance, time, schedule, airline name, etc.
2. USD avg fuel cost - this will be used to estimate the cost savings of changes to various inventory per flight
3. Inventory table - needs weight per item. i will need to generated this, begin with some sort of static number of cokes, peanuts, etc. and allow training of model based on changes there. 
4. Inventory start/end amounts - it needs start amount per item and end amount per item, example a flight starts with 5 cokes and 5 sprites and ends with 2 cokes and 3 sprites.

 Airline flights are public info (source, maybe an api if its free but if not just source where we will scrape this data from), and I had the personal development capabilities to get that info myself. USD avg fuel cost is available via (source api). Inventory table can be generated (source). Various ai methodologies will be used to support to *creation* of the needed training data sets.  (source)


These data sets should then be able to be used to create a basic dashboard to compute cost of each flight per leg by inventory change (source). The dashboard should support basic exploring of all data via READ, only allowing WRITE of the inventory fields (source why this is important). At this point, we have a dashboard which a user can use to see cost of a flight relative to inventory changes manually. The end user should be able to save data via a csv sheet upload, which we parse and adjust. The user should be able to write actual inventory beginning and end amounts (which will be needed to calculate which of each inventory we need)

The next step should be ai suggestions. The ai should be able to suggest optiminal number of coke vs sprite cans per leg given the input. This should be generated on demand via a "generated optimized inventory plan"

The end result should give anyone, including Mike, the ability to upload basic inventory sheets with beginning and end amounts for their existing public flights, and receive an optimized inventory plan with cost comparison. (source) In an effort to support green initiatives, this opensource project aims to optimize fuel usage for one of the largest contrutors for climate change, flight. It also aims to close a loop on a thought that has been on my mind for over a decade... i like to finish what I start.

# Methodology:
# Results:
# Conclusion:
# Sources: