sectors = [
    "Farmers",
    "Food Producers",
    "Distributors",
    "Pizzarias (B2C)",
    "Customers"
]

goods = [
    "Tomatoes",
    "Canned Tomatoes",
    "Flour",
    "Cheese",
    "Pizza",
    "Soft drinks",
    "Detergents",
    "Services"
]

companies = [
    # Farmers
    {
        "company_id": 1,
        "company_name": "GreenFields Farm",
        "sector": "Farmers",
        "output_good": "Tomatoes",
        "input_goods": ["Detergents", "Services"]
    },
    {
        "company_id": 2,
        "company_name": "Sunshine Growers",
        "sector": "Farmers",
        "output_good": "Tomatoes",
        "input_goods": ["Services"]
    },

    # Food Producers
    {
        "company_id": 3,
        "company_name": "TomatoMagic Co.",
        "sector": "Food Producers",
        "output_good": "Canned Tomatoes",
        "input_goods": ["Tomatoes", "Detergents", "Services"]
    },
    {
        "company_id": 4,
        "company_name": "Farm2Can Ltd.",
        "sector": "Food Producers",
        "output_good": "Canned Tomatoes",
        "input_goods": ["Tomatoes", "Services"]
    },

    # Distributors
    {
        "company_id": 5,
        "company_name": "FreshLink Logistics",
        "sector": "Distributors",
        "output_good": "Canned Tomatoes",
        "input_goods": ["Canned Tomatoes", "Services"]
    },
    {
        "company_id": 6,
        "company_name": "AgroDistrib Europe",
        "sector": "Distributors",
        "output_good": "Cheese",
        "input_goods": ["Cheese", "Services"]
    },

    # Pizzarias
    {
        "company_id": 7,
        "company_name": "Luigi's Pizzeria",
        "sector": "Pizzarias (B2C)",
        "output_good": "Pizza",
        "input_goods": ["Flour", "Cheese", "Canned Tomatoes", "Soft drinks", "Services"]
    },
    {
        "company_id": 8,
        "company_name": "Napoli Express",
        "sector": "Pizzarias (B2C)",
        "output_good": "Pizza",
        "input_goods": ["Flour", "Cheese", "Canned Tomatoes", "Soft drinks"]
    },

    # Customers
    {
        "company_id": 9,
        "company_name": "Anna Müller",
        "sector": "Customers",
        "output_good": None,
        "input_goods": ["Pizza", "Soft drinks"]
    },
    {
        "company_id": 10,
        "company_name": "Jean Dupont",
        "sector": "Customers",
        "output_good": None,
        "input_goods": ["Pizza", "Soft drinks"]
    }
]
