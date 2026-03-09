# Chapter 11: E-commerce Platform Development

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- **How** to build a complete e-commerce platform using Frappe/ERPNext
- **Why** e-commerce architecture requires specific performance optimizations
- **When** to use custom APIs vs standard ERPNext features
- **How** shopping cart, checkout, and payment processing work internally
- **Advanced patterns** for building scalable e-commerce solutions
- **Performance optimization** techniques for high-traffic online stores

## 📚 Chapter Topics

### 11.1 E-commerce Architecture Overview

**The E-commerce Platform Architecture**

Building an e-commerce platform on Frappe requires understanding how to leverage ERPNext's inventory, customer, and order management capabilities while creating a modern, performant online shopping experience.

#### Core Architecture Components

```python
# E-commerce platform architecture
class EcommercePlatform:
    def __init__(self):
        self.catalog_manager = CatalogManager()
        self.cart_manager = ShoppingCartManager()
        self.checkout_manager = CheckoutManager()
        self.payment_processor = PaymentProcessor()
        self.order_processor = OrderProcessor()
        self.inventory_manager = EcommerceInventoryManager()
        self.customer_manager = EcommerceCustomerManager()
        self.analytics_engine = EcommerceAnalytics()
        self.performance_monitor = EcommercePerformanceMonitor()
    
    def initialize_platform(self):
        """Initialize e-commerce platform components"""
        # Setup catalog
        self.catalog_manager.setup_catalog()
        
        # Configure shopping cart
        self.cart_manager.configure_cart()
        
        # Setup payment gateways
        self.payment_processor.setup_gateways()
        
        # Initialize inventory sync
        self.inventory_manager.setup_sync()
        
        # Configure customer management
        self.customer_manager.setup_customer_flow()
        
        # Setup analytics
        self.analytics_engine.setup_tracking()
        
        return {
            'status': 'initialized',
            'components': list(self.__dict__.keys())
        }

# Catalog management system
class CatalogManager:
    def __init__(self):
        self.product_cache = ProductCache()
        self.category_manager = CategoryManager()
        self.pricing_engine = PricingEngine()
        self.search_engine = ProductSearchEngine()
        self.recommendation_engine = RecommendationEngine()
    
    def setup_catalog(self):
        """Setup product catalog"""
        # Create product categories
        self.create_default_categories()
        
        # Setup product variants
        self.setup_variant_system()
        
        # Configure pricing rules
        self.pricing_engine.setup_pricing_rules()
        
        # Setup search indexing
        self.search_engine.build_search_index()
        
        # Setup recommendation system
        self.recommendation_engine.setup_recommendations()
    
    def create_default_categories(self):
        """Create default product categories"""
        categories = [
            {
                'category_name': 'Electronics',
                'parent_category': None,
                'description': 'Electronic devices and accessories',
                'image': 'electronics.jpg'
            },
            {
                'category_name': 'Computers',
                'parent_category': 'Electronics',
                'description': 'Laptops, desktops, and computer accessories',
                'image': 'computers.jpg'
            },
            {
                'category_name': 'Mobile Phones',
                'parent_category': 'Electronics',
                'description': 'Smartphones and mobile accessories',
                'image': 'mobile.jpg'
            },
            {
                'category_name': 'Clothing',
                'parent_category': None,
                'description': 'Apparel and fashion accessories',
                'image': 'clothing.jpg'
            },
            {
                'category_name': 'Home & Garden',
                'parent_category': None,
                'description': 'Home improvement and garden supplies',
                'image': 'home.jpg'
            }
        ]
        
        for category_data in categories:
            if not frappe.db.exists('Item Group', category_data['category_name']):
                category = frappe.new_doc('Item Group')
                category.item_group_name = category_data['category_name']
                category.parent_item_group = category_data['parent_category']
                category.description = category_data['description']
                category.image = category_data['image']
                category.is_group = 0
                category.insert()
    
    def get_product_details(self, item_code, include_variants=True):
        """Get comprehensive product details"""
        # Try cache first
        cached_product = self.product_cache.get_product(item_code)
        if cached_product:
            return cached_product
        
        # Load from database
        product = frappe.get_doc('Item', item_code)
        
        product_data = {
            'item_code': product.name,
            'item_name': product.item_name,
            'description': product.description,
            'item_group': product.item_group,
            'brand': product.brand,
            'stock_uom': product.stock_uom,
            'image': product.image,
            'website_specifications': product.website_specifications or {},
            'website_long_description': product.website_long_description,
            'show_in_website': product.show_in_website,
            'website_warehouse': product.website_warehouse,
            'disabled': product.disabled
        }
        
        # Get pricing
        product_data['pricing'] = self.pricing_engine.get_product_pricing(item_code)
        
        # Get inventory
        product_data['inventory'] = self.get_product_inventory(item_code)
        
        # Get variants if requested
        if include_variants:
            product_data['variants'] = self.get_product_variants(item_code)
        
        # Get related products
        product_data['related_products'] = self.recommendation_engine.get_related_products(item_code)
        
        # Get reviews
        product_data['reviews'] = self.get_product_reviews(item_code)
        
        # Cache product data
        self.product_cache.cache_product(item_code, product_data)
        
        return product_data
    
    def get_product_inventory(self, item_code):
        """Get product inventory information"""
        warehouse = frappe.db.get_single_value('Website Settings', 'default_warehouse')
        
        # Get actual stock
        actual_qty = frappe.db.get_value('Bin', 
                                       {'item_code': item_code, 'warehouse': warehouse}, 
                                       'actual_qty') or 0
        
        # Get reserved stock
        reserved_qty = frappe.db.get_value('Bin', 
                                          {'item_code': item_code, 'warehouse': warehouse}, 
                                          'reserved_qty') or 0
        
        # Get available stock
        available_qty = actual_qty - reserved_qty
        
        # Get stock status
        if available_qty <= 0:
            stock_status = 'Out of Stock'
        elif available_qty < 10:
            stock_status = 'Low Stock'
        else:
            stock_status = 'In Stock'
        
        return {
            'actual_qty': actual_qty,
            'reserved_qty': reserved_qty,
            'available_qty': available_qty,
            'stock_status': stock_status,
            'warehouse': warehouse
        }
    
    def get_product_variants(self, item_code):
        """Get product variants"""
        variants = []
        
        # Get variant items
        variant_items = frappe.get_all('Item', 
                                      filters={'variant_of': item_code, 'disabled': 0},
                                      fields=['name', 'item_name', 'description', 'image'])
        
        for variant in variant_items:
            variant_data = {
                'item_code': variant.name,
                'item_name': variant.item_name,
                'description': variant.description,
                'image': variant.image,
                'attributes': self.get_variant_attributes(variant.name),
                'pricing': self.pricing_engine.get_product_pricing(variant.name),
                'inventory': self.get_product_inventory(variant.name)
            }
            variants.append(variant_data)
        
        return variants
    
    def get_variant_attributes(self, variant_item_code):
        """Get variant attributes"""
        attributes = {}
        
        # Get item attribute values
        attribute_values = frappe.get_all('Item Variant Attribute',
                                         filters={'parent': variant_item_code},
                                         fields=['attribute', 'attribute_value'])
        
        for attr in attribute_values:
            attributes[attr.attribute] = attr.attribute_value
        
        return attributes
    
    def get_product_reviews(self, item_code):
        """Get product reviews"""
        reviews = frappe.get_all('Product Review',
                                 filters={'item_code': item_code, 'published': 1},
                                 fields=['rating', 'review_title', 'review_comment', 'customer_name', 'creation'],
                                 order_by='creation desc')
        
        return reviews
    
    def search_products(self, query, category=None, brand=None, price_range=None, sort_by='relevance'):
        """Search products with advanced filtering"""
        # Use search engine
        search_results = self.search_engine.search_products(
            query=query,
            category=category,
            brand=brand,
            price_range=price_range,
            sort_by=sort_by
        )
        
        # Get product details for search results
        products = []
        for result in search_results:
            product_data = self.get_product_details(result['item_code'], include_variants=False)
            product_data['relevance_score'] = result['relevance_score']
            products.append(product_data)
        
        return products
    
    def get_category_products(self, category, limit=20, page=1):
        """Get products by category"""
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get products in category
        products = frappe.get_all('Item',
                                  filters={'item_group': category, 'show_in_website': 1, 'disabled': 0},
                                  fields=['name', 'item_name', 'description', 'image', 'brand'],
                                  limit=limit,
                                  start=offset,
                                  order_by='creation desc')
        
        # Get detailed product data
        product_list = []
        for product in products:
            product_data = self.get_product_details(product.name, include_variants=False)
            product_list.append(product_data)
        
        return product_list

# Shopping cart management
class ShoppingCartManager:
    def __init__(self):
        self.cart_cache = CartCache()
        self.pricing_calculator = CartPricingCalculator()
        self.inventory_checker = InventoryChecker()
    
    def configure_cart(self):
        """Configure shopping cart settings"""
        # Setup cart session management
        self.setup_cart_sessions()
        
        # Configure cart persistence
        self.setup_cart_persistence()
        
        # Setup cart analytics
        self.setup_cart_analytics()
    
    def setup_cart_sessions(self):
        """Setup cart session management"""
        # Create cart session table if not exists
        if not frappe.db.exists('DocType', 'Cart Session'):
            self.create_cart_session_doctype()
    
    def create_cart_session_doctype(self):
        """Create cart session DocType"""
        doctype = frappe.new_doc('DocType')
        doctype.name = 'Cart Session'
        doctype.module = 'Ecommerce'
        doctype.custom = 1
        doctype.is_submittable = 0
        doctype.istable = 0
        
        # Add fields
        fields = [
            {'fieldname': 'session_id', 'fieldtype': 'Data', 'label': 'Session ID', 'reqd': 1, 'unique': 1},
            {'fieldname': 'customer', 'fieldtype': 'Link', 'label': 'Customer', 'options': 'Customer'},
            {'fieldname': 'items', 'fieldtype': 'Table', 'label': 'Cart Items', 'options': 'Cart Item'},
            {'fieldname': 'total_amount', 'fieldtype': 'Currency', 'label': 'Total Amount'},
            {'fieldname': 'created_at', 'fieldtype': 'Datetime', 'label': 'Created At'},
            {'fieldname': 'updated_at', 'fieldtype': 'Datetime', 'label': 'Updated At'},
            {'fieldname': 'status', 'fieldtype': 'Select', 'label': 'Status', 'options': 'Active\nExpired\nConverted'}
        ]
        
        for field in fields:
            doctype.append('fields', field)
        
        doctype.insert()
    
    def get_cart(self, session_id=None, customer=None):
        """Get shopping cart"""
        if not session_id:
            session_id = self.generate_session_id()
        
        # Try cache first
        cached_cart = self.cart_cache.get_cart(session_id)
        if cached_cart:
            return cached_cart
        
        # Get cart from database
        cart = self.get_cart_from_database(session_id, customer)
        
        if not cart:
            # Create new cart
            cart = self.create_cart(session_id, customer)
        
        # Validate cart items
        cart = self.validate_cart_items(cart)
        
        # Calculate pricing
        cart = self.calculate_cart_pricing(cart)
        
        # Cache cart
        self.cart_cache.cache_cart(session_id, cart)
        
        return cart
    
    def generate_session_id(self):
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_cart_from_database(self, session_id, customer):
        """Get cart from database"""
        cart_doc = frappe.get_all('Cart Session',
                                 filters={'session_id': session_id, 'status': 'Active'},
                                 fields=['name', 'session_id', 'customer', 'total_amount', 'created_at'])
        
        if cart_doc:
            cart = cart_doc[0]
            
            # Get cart items
            items = frappe.get_all('Cart Item',
                                  filters={'parent': cart.name},
                                  fields=['item_code', 'item_name', 'qty', 'rate', 'amount', 'image'])
            
            cart['items'] = items
            return cart
        
        return None
    
    def create_cart(self, session_id, customer):
        """Create new cart"""
        cart = frappe.new_doc('Cart Session')
        cart.session_id = session_id
        cart.customer = customer
        cart.status = 'Active'
        cart.created_at = frappe.utils.now()
        cart.updated_at = frappe.utils.now()
        cart.insert()
        
        return {
            'name': cart.name,
            'session_id': session_id,
            'customer': customer,
            'items': [],
            'total_amount': 0,
            'created_at': cart.created_at
        }
    
    def add_to_cart(self, session_id, item_code, qty=1, variant=None):
        """Add item to cart"""
        # Get cart
        cart = self.get_cart(session_id)
        
        # Check inventory
        inventory_check = self.inventory_checker.check_inventory(item_code, qty)
        if not inventory_check['available']:
            raise Exception(f"Item {item_code} is not available in requested quantity")
        
        # Check if item already in cart
        existing_item = next((item for item in cart['items'] if item['item_code'] == item_code), None)
        
        if existing_item:
            # Update quantity
            new_qty = existing_item['qty'] + qty
            
            # Check inventory again
            inventory_check = self.inventory_checker.check_inventory(item_code, new_qty)
            if not inventory_check['available']:
                raise Exception(f"Cannot add {item_code} to cart. Insufficient inventory.")
            
            # Update cart item
            self.update_cart_item(cart['name'], existing_item['item_code'], new_qty)
        else:
            # Add new item to cart
            self.add_cart_item(cart['name'], item_code, qty)
        
        # Clear cache
        self.cart_cache.clear_cart(session_id)
        
        # Return updated cart
        return self.get_cart(session_id)
    
    def add_cart_item(self, cart_name, item_code, qty):
        """Add item to cart database"""
        # Get item details
        item = frappe.get_doc('Item', item_code)
        
        # Get pricing
        pricing = frappe.get_doc('Item Price', {'item_code': item_code, 'price_list': 'Standard Selling'})
        
        # Create cart item
        cart_item = frappe.new_doc('Cart Item')
        cart_item.parent = cart_name
        cart_item.parenttype = 'Cart Session'
        cart_item.parentfield = 'items'
        cart_item.item_code = item_code
        cart_item.item_name = item.item_name
        cart_item.qty = qty
        cart_item.rate = pricing.price_list_rate
        cart_item.amount = qty * pricing.price_list_rate
        cart_item.image = item.image
        cart_item.insert()
        
        # Update cart total
        self.update_cart_total(cart_name)
    
    def update_cart_item(self, cart_name, item_code, qty):
        """Update cart item quantity"""
        # Find cart item
        cart_item = frappe.get_doc('Cart Item', {'parent': cart_name, 'item_code': item_code})
        
        if cart_item:
            # Update quantity and amount
            cart_item.qty = qty
            cart_item.amount = qty * cart_item.rate
            cart_item.save()
            
            # Update cart total
            self.update_cart_total(cart_name)
    
    def update_cart_total(self, cart_name):
        """Update cart total amount"""
        # Calculate total from items
        items = frappe.get_all('Cart Item',
                              filters={'parent': cart_name},
                              fields=['amount'])
        
        total = sum(item['amount'] for item in items)
        
        # Update cart
        cart = frappe.get_doc('Cart Session', cart_name)
        cart.total_amount = total
        cart.updated_at = frappe.utils.now()
        cart.save()
    
    def remove_from_cart(self, session_id, item_code):
        """Remove item from cart"""
        cart = self.get_cart(session_id)
        
        # Find and remove item
        cart_item = frappe.get_doc('Cart Item', {'parent': cart['name'], 'item_code': item_code})
        if cart_item:
            cart_item.delete()
            
            # Update cart total
            self.update_cart_total(cart['name'])
            
            # Clear cache
            self.cart_cache.clear_cart(session_id)
        
        return self.get_cart(session_id)
    
    def validate_cart_items(self, cart):
        """Validate cart items"""
        valid_items = []
        
        for item in cart['items']:
            # Check if item is still available
            if not frappe.db.exists('Item', item['item_code']) or frappe.db.get_value('Item', item['item_code'], 'disabled'):
                continue  # Skip disabled/non-existent items
            
            # Check inventory
            inventory_check = self.inventory_checker.check_inventory(item['item_code'], item['qty'])
            if not inventory_check['available']:
                # Update quantity to available amount
                item['qty'] = inventory_check['available_qty']
                item['amount'] = item['qty'] * item['rate']
            
            valid_items.append(item)
        
        cart['items'] = valid_items
        return cart
    
    def calculate_cart_pricing(self, cart):
        """Calculate cart pricing with discounts and taxes"""
        # Calculate subtotal
        subtotal = sum(item['amount'] for item in cart['items'])
        
        # Apply discounts
        discounts = self.calculate_cart_discounts(cart)
        discount_amount = sum(discount['amount'] for discount in discounts)
        
        # Calculate taxes
        taxes = self.calculate_cart_taxes(cart, subtotal - discount_amount)
        tax_amount = sum(tax['amount'] for tax in taxes)
        
        # Calculate total
        total = subtotal - discount_amount + tax_amount
        
        cart['subtotal'] = subtotal
        cart['discounts'] = discounts
        cart['discount_amount'] = discount_amount
        cart['taxes'] = taxes
        cart['tax_amount'] = tax_amount
        cart['total_amount'] = total
        
        return cart
    
    def calculate_cart_discounts(self, cart):
        """Calculate cart discounts"""
        discounts = []
        
        # Check for promotional discounts
        promo_discounts = self.get_promotional_discounts(cart)
        discounts.extend(promo_discounts)
        
        # Check for customer discounts
        if cart['customer']:
            customer_discounts = self.get_customer_discounts(cart['customer'], cart)
            discounts.extend(customer_discounts)
        
        return discounts
    
    def get_promotional_discounts(self, cart):
        """Get promotional discounts"""
        discounts = []
        
        # Check for active promotions
        promotions = frappe.get_all('Promotion',
                                    filters={'active': 1, 'from_date': ['<=', frappe.utils.nowdate()],
                                            'to_date': ['>=', frappe.utils.nowdate()]},
                                    fields=['name', 'discount_type', 'discount_amount', 'min_order_value'])
        
        for promo in promotions:
            if cart['subtotal'] >= promo.min_order_value:
                discount = {
                    'promotion': promo.name,
                    'type': promo.discount_type,
                    'amount': promo.discount_amount if promo.discount_type == 'Fixed' else cart['subtotal'] * promo.discount_amount / 100
                }
                discounts.append(discount)
        
        return discounts
    
    def get_customer_discounts(self, customer, cart):
        """Get customer-specific discounts"""
        discounts = []
        
        # Get customer discount rules
        customer_discounts = frappe.get_all('Customer Discount',
                                           filters={'customer': customer, 'active': 1},
                                           fields=['discount_type', 'discount_amount', 'min_order_value'])
        
        for discount_rule in customer_discounts:
            if cart['subtotal'] >= discount_rule.min_order_value:
                discount = {
                    'customer_discount': discount_rule.name,
                    'type': discount_rule.discount_type,
                    'amount': discount_rule.discount_amount if discount_rule.discount_type == 'Fixed' else cart['subtotal'] * discount_rule.discount_amount / 100
                }
                discounts.append(discount)
        
        return discounts
    
    def calculate_cart_taxes(self, cart, taxable_amount):
        """Calculate cart taxes"""
        taxes = []
        
        # Get tax templates
        tax_templates = frappe.get_all('Sales Taxes and Charges Template',
                                       fields=['name', 'taxes'])
        
        for template in tax_templates:
            template_taxes = json.loads(template.taxes or '[]')
            
            for tax in template_taxes:
                if tax.get('charge_type') == 'On Net Total':
                    tax_amount = taxable_amount * tax.get('rate', 0) / 100
                    
                    taxes.append({
                        'tax_name': tax.get('account_head'),
                        'rate': tax.get('rate', 0),
                        'amount': tax_amount
                    })
        
        return taxes

# Checkout management
class CheckoutManager:
    def __init__(self):
        self.address_manager = AddressManager()
        self.shipping_manager = ShippingManager()
        self.payment_manager = PaymentManager()
        self.order_creator = OrderCreator()
    
    def initiate_checkout(self, session_id):
        """Initiate checkout process"""
        # Get cart
        cart_manager = ShoppingCartManager()
        cart = cart_manager.get_cart(session_id)
        
        if not cart['items']:
            raise Exception("Cart is empty")
        
        # Create checkout session
        checkout_session = self.create_checkout_session(cart)
        
        return checkout_session
    
    def create_checkout_session(self, cart):
        """Create checkout session"""
        checkout = frappe.new_doc('Checkout Session')
        checkout.cart_session = cart['name']
        checkout.customer = cart['customer']
        checkout.status = 'Pending'
        checkout.created_at = frappe.utils.now()
        checkout.insert()
        
        checkout_data = {
            'checkout_id': checkout.name,
            'cart': cart,
            'customer': cart['customer'],
            'steps': self.get_checkout_steps(),
            'current_step': 1
        }
        
        return checkout_data
    
    def get_checkout_steps(self):
        """Get checkout process steps"""
        return [
            {
                'step': 1,
                'name': 'Customer Information',
                'title': 'Customer Details',
                'completed': False
            },
            {
                'step': 2,
                'name': 'Shipping Address',
                'title': 'Shipping Information',
                'completed': False
            },
            {
                'step': 3,
                'name': 'Shipping Method',
                'title': 'Shipping Method',
                'completed': False
            },
            {
                'step': 4,
                'name': 'Payment Method',
                'title': 'Payment Information',
                'completed': False
            },
            {
                'step': 5,
                'name': 'Review',
                'title': 'Review Order',
                'completed': False
            }
        ]
    
    def update_checkout_step(self, checkout_id, step_data):
        """Update checkout step data"""
        checkout = frappe.get_doc('Checkout Session', checkout_id)
        
        # Update step-specific data
        step_name = step_data.get('step_name')
        
        if step_name == 'Customer Information':
            self.update_customer_info(checkout, step_data)
        elif step_name == 'Shipping Address':
            self.update_shipping_address(checkout, step_data)
        elif step_name == 'Shipping Method':
            self.update_shipping_method(checkout, step_data)
        elif step_name == 'Payment Method':
            self.update_payment_method(checkout, step_data)
        
        checkout.save()
        
        return self.get_checkout_data(checkout_id)
    
    def update_customer_info(self, checkout, data):
        """Update customer information"""
        customer_data = data.get('customer_data', {})
        
        if checkout.customer:
            # Update existing customer
            customer = frappe.get_doc('Customer', checkout.customer)
            customer.customer_name = customer_data.get('customer_name', customer.customer_name)
            customer.email_id = customer_data.get('email_id', customer.email_id)
            customer.phone = customer_data.get('phone', customer.phone)
            customer.save()
        else:
            # Create new customer
            customer = frappe.new_doc('Customer')
            customer.customer_name = customer_data.get('customer_name')
            customer.email_id = customer_data.get('email_id')
            customer.phone = customer_data.get('phone')
            customer.customer_type = 'Individual'
            customer.insert()
            
            checkout.customer = customer.name
        
        checkout.customer_info = json.dumps(customer_data)
    
    def update_shipping_address(self, checkout, data):
        """Update shipping address"""
        address_data = data.get('address_data', {})
        
        if address_data.get('address_id'):
            # Use existing address
            checkout.shipping_address = address_data['address_id']
        else:
            # Create new address
            address = frappe.new_doc('Address')
            address.address_title = address_data.get('address_title')
            address.address_line1 = address_data.get('address_line1')
            address.address_line2 = address_data.get('address_line2')
            address.city = address_data.get('city')
            address.state = address_data.get('state')
            address.country = address_data.get('country')
            address.pincode = address_data.get('pincode')
            address.link_doctype = 'Customer'
            address.link_name = checkout.customer
            address.insert()
            
            checkout.shipping_address = address.name
        
        checkout.shipping_address_data = json.dumps(address_data)
    
    def update_shipping_method(self, checkout, data):
        """Update shipping method"""
        shipping_data = data.get('shipping_data', {})
        
        checkout.shipping_method = shipping_data.get('shipping_method')
        checkout.shipping_carrier = shipping_data.get('shipping_carrier')
        checkout.shipping_cost = shipping_data.get('shipping_cost', 0)
    
    def update_payment_method(self, checkout, data):
        """Update payment method"""
        payment_data = data.get('payment_data', {})
        
        checkout.payment_method = payment_data.get('payment_method')
        checkout.payment_gateway = payment_data.get('payment_gateway')
        checkout.payment_details = json.dumps(payment_data)
    
    def calculate_checkout_totals(self, checkout_id):
        """Calculate checkout totals including shipping"""
        checkout = frappe.get_doc('Checkout Session', checkout_id)
        
        # Get cart
        cart_manager = ShoppingCartManager()
        cart = cart_manager.get_cart(checkout.cart_session)
        
        # Start with cart total
        subtotal = cart['subtotal']
        
        # Add shipping cost
        shipping_cost = checkout.shipping_cost or 0
        
        # Apply discounts
        discounts = self.calculate_checkout_discounts(checkout, cart)
        discount_amount = sum(discount['amount'] for discount in discounts)
        
        # Calculate taxes
        taxable_amount = subtotal + shipping_cost - discount_amount
        taxes = self.calculate_checkout_taxes(checkout, taxable_amount)
        tax_amount = sum(tax['amount'] for tax in taxes)
        
        # Calculate grand total
        grand_total = subtotal + shipping_cost - discount_amount + tax_amount
        
        return {
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'discounts': discounts,
            'discount_amount': discount_amount,
            'taxes': taxes,
            'tax_amount': tax_amount,
            'grand_total': grand_total
        }
    
    def place_order(self, checkout_id):
        """Place order from checkout"""
        checkout = frappe.get_doc('Checkout Session', checkout_id)
        
        # Validate checkout
        if not self.validate_checkout(checkout):
            raise Exception("Checkout validation failed")
        
        # Create order
        order = self.order_creator.create_order_from_checkout(checkout)
        
        # Update checkout status
        checkout.status = 'Completed'
        checkout.order_id = order.name
        checkout.completed_at = frappe.utils.now()
        checkout.save()
        
        # Clear cart
        cart_manager = ShoppingCartManager()
        cart_manager.clear_cart(checkout.cart_session)
        
        return order

# Payment processing
class PaymentProcessor:
    def __init__(self):
        self.gateways = {}
        self.transaction_manager = PaymentTransactionManager()
        self.setup_gateways()
    
    def setup_gateways(self):
        """Setup payment gateways"""
        self.gateways['stripe'] = StripeGateway()
        self.gateways['paypal'] = PayPalGateway()
        self.gateways['razorpay'] = RazorpayGateway()
        self.gateways['cash_on_delivery'] = CashOnDeliveryGateway()
    
    def process_payment(self, payment_data):
        """Process payment through appropriate gateway"""
        gateway_name = payment_data.get('gateway')
        gateway = self.gateways.get(gateway_name)
        
        if not gateway:
            raise Exception(f"Payment gateway {gateway_name} not found")
        
        # Create payment transaction
        transaction = self.transaction_manager.create_transaction(payment_data)
        
        try:
            # Process payment
            result = gateway.process_payment(payment_data, transaction.name)
            
            # Update transaction
            if result['success']:
                transaction.status = 'Completed'
                transaction.gateway_transaction_id = result['transaction_id']
                transaction.gateway_response = json.dumps(result)
                transaction.completed_at = frappe.utils.now()
            else:
                transaction.status = 'Failed'
                transaction.error_message = result.get('error', 'Payment failed')
            
            transaction.save()
            
            return {
                'success': result['success'],
                'transaction_id': transaction.name,
                'gateway_transaction_id': result.get('transaction_id'),
                'error': result.get('error')
            }
            
        except Exception as e:
            transaction.status = 'Failed'
            transaction.error_message = str(e)
            transaction.save()
            raise e
    
    def refund_payment(self, transaction_id, amount=None):
        """Process payment refund"""
        transaction = frappe.get_doc('Payment Transaction', transaction_id)
        
        if transaction.status != 'Completed':
            raise Exception("Cannot refund non-completed transaction")
        
        gateway = self.gateways.get(transaction.gateway)
        
        if not gateway:
            raise Exception(f"Payment gateway {transaction.gateway} not found")
        
        # Process refund
        result = gateway.refund_payment(transaction.gateway_transaction_id, amount)
        
        if result['success']:
            # Create refund transaction
            refund_transaction = self.transaction_manager.create_refund_transaction(transaction, amount, result)
            
            return {
                'success': True,
                'refund_transaction_id': refund_transaction.name,
                'gateway_refund_id': result.get('refund_id')
            }
        else:
            return {
                'success': False,
                'error': result.get('error')
            }

# Payment gateway base class
class PaymentGateway:
    def __init__(self):
        self.config = self.get_gateway_config()
    
    def get_gateway_config(self):
        """Get gateway configuration"""
        return {}
    
    def process_payment(self, payment_data, transaction_id):
        """Process payment - to be implemented by subclasses"""
        raise NotImplementedError
    
    def refund_payment(self, gateway_transaction_id, amount=None):
        """Refund payment - to be implemented by subclasses"""
        raise NotImplementedError

# Stripe gateway implementation
class StripeGateway(PaymentGateway):
    def get_gateway_config(self):
        """Get Stripe configuration"""
        return {
            'api_key': frappe.db.get_single_value('Stripe Settings', 'api_key'),
            'secret_key': frappe.db.get_single_value('Stripe Settings', 'secret_key'),
            'webhook_secret': frappe.db.get_single_value('Stripe Settings', 'webhook_secret')
        }
    
    def process_payment(self, payment_data, transaction_id):
        """Process Stripe payment"""
        try:
            import stripe
            
            stripe.api_key = self.config['secret_key']
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(payment_data['amount'] * 100),  # Convert to cents
                currency=payment_data['currency'].lower(),
                payment_method=payment_data['payment_method_id'],
                confirmation_method='manual',
                confirm=True,
                metadata={'transaction_id': transaction_id}
            )
            
            if intent.status == 'succeeded':
                return {
                    'success': True,
                    'transaction_id': intent.id,
                    'status': intent.status
                }
            else:
                return {
                    'success': False,
                    'error': f"Payment failed: {intent.status}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, gateway_transaction_id, amount=None):
        """Process Stripe refund"""
        try:
            import stripe
            
            stripe.api_key = self.config['secret_key']
            
            refund_params = {'payment_intent': gateway_transaction_id}
            if amount:
                refund_params['amount'] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

### 11.2 Building the Online Store Frontend

#### Frontend Architecture and Components

```javascript
// E-commerce frontend architecture
class EcommerceFrontend {
    constructor() {
        this.catalog = new ProductCatalog();
        this.cart = new ShoppingCart();
        this.checkout = new CheckoutProcess();
        this.user = new UserManager();
        this.search = new ProductSearch();
        this.analytics = new AnalyticsTracker();
        this.performance = new PerformanceMonitor();
        
        this.initialize_app();
    }
    
    initialize_app() {
        // Initialize routing
        this.setup_routing();
        
        // Setup global state management
        this.setup_state_management();
        
        // Initialize components
        this.setup_components();
        
        // Setup event listeners
        this.setup_event_listeners();
        
        // Track page view
        this.analytics.track_page_view();
    }
    
    setup_routing() {
        // Setup client-side routing
        this.routes = {
            '/': 'home',
            '/products': 'product_list',
            '/product/:id': 'product_detail',
            '/category/:id': 'category_products',
            '/cart': 'shopping_cart',
            '/checkout': 'checkout',
            '/account': 'user_account',
            '/orders': 'order_history',
            '/search': 'search_results'
        };
        
        // Initialize router
        this.router = new Router(this.routes);
        this.router.init();
    }
    
    setup_state_management() {
        // Setup global state
        this.state = {
            user: null,
            cart: null,
            products: [],
            categories: [],
            loading: false,
            error: null
        };
        
        // Setup state subscribers
        this.state_subscribers = [];
    }
    
    setup_components() {
        // Initialize main components
        this.components = {
            header: new HeaderComponent(),
            navigation: new NavigationComponent(),
            product_grid: new ProductGridComponent(),
            product_detail: new ProductDetailComponent(),
            cart_sidebar: new CartSidebarComponent(),
            checkout_form: new CheckoutFormComponent(),
            user_menu: new UserMenuComponent()
        };
        
        // Mount components
        this.mount_components();
    }
    
    mount_components() {
        // Mount header
        this.components.header.mount('#header');
        
        // Mount navigation
        this.components.navigation.mount('#navigation');
        
        // Mount main content area
        this.mount_main_content();
        
        // Mount cart sidebar
        this.components.cart_sidebar.mount('#cart-sidebar');
    }
    
    mount_main_content() {
        // Dynamic content mounting based on route
        this.router.on('route:changed', (route) => {
            this.render_page(route);
        });
    }
    
    render_page(route) {
        const content_area = document.getElementById('main-content');
        
        switch(route.name) {
            case 'home':
                this.render_home_page(content_area);
                break;
            case 'product_list':
                this.render_product_list_page(content_area, route.params);
                break;
            case 'product_detail':
                this.render_product_detail_page(content_area, route.params);
                break;
            case 'shopping_cart':
                this.render_cart_page(content_area);
                break;
            case 'checkout':
                this.render_checkout_page(content_area);
                break;
            default:
                this.render_404_page(content_area);
        }
    }
    
    render_home_page(container) {
        container.innerHTML = `
            <div class="home-page">
                <section class="hero-section">
                    <div class="hero-content">
                        <h1>Welcome to Our Store</h1>
                        <p>Discover amazing products at great prices</p>
                        <button class="btn btn-primary" onclick="ecommerce.catalog.browse_products()">
                            Shop Now
                        </button>
                    </div>
                </section>
                
                <section class="featured-products">
                    <h2>Featured Products</h2>
                    <div id="featured-products-grid" class="product-grid"></div>
                </section>
                
                <section class="categories">
                    <h2>Shop by Category</h2>
                    <div id="categories-grid" class="category-grid"></div>
                </section>
            </div>
        `;
        
        // Load featured products
        this.load_featured_products();
        
        // Load categories
        this.load_categories();
    }
    
    async load_featured_products() {
        try {
            this.set_loading(true);
            
            const products = await this.catalog.get_featured_products();
            
            const grid = document.getElementById('featured-products-grid');
            grid.innerHTML = this.components.product_grid.render(products);
            
            this.set_loading(false);
            
        } catch (error) {
            this.handle_error(error);
        }
    }
    
    async load_categories() {
        try {
            const categories = await this.catalog.get_categories();
            
            const grid = document.getElementById('categories-grid');
            grid.innerHTML = this.render_categories(categories);
            
        } catch (error) {
            this.handle_error(error);
        }
    }
    
    render_categories(categories) {
        return categories.map(category => `
            <div class="category-card" onclick="ecommerce.catalog.browse_category('${category.name}')">
                <img src="${category.image}" alt="${category.name}">
                <h3>${category.name}</h3>
                <p>${category.description}</p>
            </div>
        `).join('');
    }
    
    render_product_list_page(container, params) {
        container.innerHTML = `
            <div class="product-list-page">
                <div class="page-header">
                    <h1>Products</h1>
                    <div class="filters-bar">
                        <select id="category-filter" onchange="ecommerce.search.filter_by_category(this.value)">
                            <option value="">All Categories</option>
                        </select>
                        <select id="sort-filter" onchange="ecommerce.search.sort_products(this.value)">
                            <option value="relevance">Sort by Relevance</option>
                            <option value="price_low">Price: Low to High</option>
                            <option value="price_high">Price: High to Low</option>
                            <option value="name">Name: A to Z</option>
                        </select>
                        <div class="search-box">
                            <input type="text" placeholder="Search products..." 
                                   onkeyup="ecommerce.search.search_products(this.value)">
                        </div>
                    </div>
                </div>
                
                <div class="products-container">
                    <div class="filters-sidebar">
                        <div class="filter-section">
                            <h3>Price Range</h3>
                            <div class="price-range-filter">
                                <input type="number" id="min-price" placeholder="Min">
                                <input type="number" id="max-price" placeholder="Max">
                                <button onclick="ecommerce.search.apply_price_filter()">Apply</button>
                            </div>
                        </div>
                        
                        <div class="filter-section">
                            <h3>Brand</h3>
                            <div class="brand-filter">
                                <!-- Brands will be loaded dynamically -->
                            </div>
                        </div>
                    </div>
                    
                    <div class="products-grid" id="products-grid">
                        <!-- Products will be loaded here -->
                    </div>
                </div>
                
                <div class="pagination" id="pagination">
                    <!-- Pagination will be loaded here -->
                </div>
            </div>
        `;
        
        // Load products
        this.load_product_list(params);
        
        // Load filters
        this.load_filters();
    }
    
    async load_product_list(params) {
        try {
            this.set_loading(true);
            
            const category = params.category || '';
            const products = await this.catalog.get_products({ category });
            
            const grid = document.getElementById('products-grid');
            grid.innerHTML = this.components.product_grid.render(products);
            
            // Setup pagination
            this.setup_pagination(products.total_count, products.page, products.per_page);
            
            this.set_loading(false);
            
        } catch (error) {
            this.handle_error(error);
        }
    }
    
    render_product_detail_page(container, params) {
        container.innerHTML = `
            <div class="product-detail-page">
                <div class="product-container">
                    <div class="product-images">
                        <div class="main-image">
                            <img id="main-product-image" src="" alt="">
                        </div>
                        <div class="thumbnail-images" id="thumbnail-images">
                            <!-- Thumbnails will be loaded here -->
                        </div>
                    </div>
                    
                    <div class="product-info">
                        <h1 id="product-name"></h1>
                        <div class="product-meta">
                            <span class="brand" id="product-brand"></span>
                            <span class="sku" id="product-sku"></span>
                        </div>
                        
                        <div class="price-section">
                            <div class="current-price" id="current-price"></div>
                            <div class="original-price" id="original-price"></div>
                            <div class="discount" id="discount"></div>
                        </div>
                        
                        <div class="product-description" id="product-description"></div>
                        
                        <div class="product-variants" id="product-variants">
                            <!-- Product variants will be loaded here -->
                        </div>
                        
                        <div class="add-to-cart-section">
                            <div class="quantity-selector">
                                <button onclick="ecommerce.cart.decrease_quantity()">-</button>
                                <input type="number" id="quantity" value="1" min="1" max="">
                                <button onclick="ecommerce.cart.increase_quantity()">+</button>
                            </div>
                            
                            <button class="btn btn-primary btn-lg" onclick="ecommerce.cart.add_to_cart()">
                                Add to Cart
                            </button>
                            
                            <button class="btn btn-secondary btn-lg" onclick="ecommerce.cart.buy_now()">
                                Buy Now
                            </button>
                        </div>
                        
                        <div class="product-features">
                            <div class="feature">
                                <i class="fas fa-shipping-fast"></i>
                                <span>Free Shipping</span>
                            </div>
                            <div class="feature">
                                <i class="fas fa-shield-alt"></i>
                                <span>Secure Payment</span>
                            </div>
                            <div class="feature">
                                <i classfas fa-undo"></i>
                                <span>Easy Returns</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="product-tabs">
                    <div class="tab-nav">
                        <button class="tab-btn active" onclick="ecommerce.catalog.show_tab('description')">
                            Description
                        </button>
                        <button class="tab-btn" onclick="ecommerce.catalog.show_tab('specifications')">
                            Specifications
                        </button>
                        <button class="tab-btn" onclick="ecommerce.catalog.show_tab('reviews')">
                            Reviews
                        </button>
                    </div>
                    
                    <div class="tab-content">
                        <div class="tab-pane active" id="description-tab">
                            <div id="product-long-description"></div>
                        </div>
                        <div class="tab-pane" id="specifications-tab">
                            <div id="product-specifications"></div>
                        </div>
                        <div class="tab-pane" id="reviews-tab">
                            <div id="product-reviews"></div>
                        </div>
                    </div>
                </div>
                
                <div class="related-products">
                    <h2>Related Products</h2>
                    <div class="products-grid" id="related-products-grid">
                        <!-- Related products will be loaded here -->
                    </div>
                </div>
            </div>
        `;
        
        // Load product details
        this.load_product_detail(params.id);
    }
    
    async load_product_detail(product_id) {
        try {
            this.set_loading(true);
            
            const product = await this.catalog.get_product_details(product_id);
            
            // Update product information
            document.getElementById('product-name').textContent = product.item_name;
            document.getElementById('product-brand').textContent = product.brand || '';
            document.getElementById('product-sku').textContent = product.item_code;
            document.getElementById('current-price').textContent = this.format_currency(product.pricing.price);
            document.getElementById('product-description').textContent = product.description;
            
            // Update images
            this.update_product_images(product);
            
            // Update variants
            this.update_product_variants(product);
            
            // Update long description
            document.getElementById('product-long-description').innerHTML = product.website_long_description || '';
            
            // Update specifications
            this.update_product_specifications(product);
            
            // Load reviews
            this.load_product_reviews(product);
            
            // Load related products
            this.load_related_products(product);
            
            // Set max quantity based on inventory
            const quantity_input = document.getElementById('quantity');
            quantity_input.max = product.inventory.available_qty;
            
            this.set_loading(false);
            
        } catch (error) {
            this.handle_error(error);
        }
    }
    
    update_product_images(product) {
        const main_image = document.getElementById('main-product-image');
        const thumbnail_container = document.getElementById('thumbnail-images');
        
        if (product.image) {
            main_image.src = `/files/${product.image}`;
        }
        
        // Add thumbnails (including main image)
        const images = [product.image].filter(Boolean);
        
        thumbnail_container.innerHTML = images.map((image, index) => `
            <img src="/files/${image}" alt="Product image ${index + 1}" 
                 onclick="ecommerce.catalog.change_main_image('/files/${image}')"
                 class="${index === 0 ? 'active' : ''}">
        `).join('');
    }
    
    update_product_variants(product) {
        const variants_container = document.getElementById('product-variants');
        
        if (product.variants && product.variants.length > 0) {
            variants_container.innerHTML = `
                <h3>Select Options</h3>
                <div class="variant-options">
                    ${product.variants.map(variant => `
                        <div class="variant-option">
                            <label>${Object.keys(variant.attributes).join(', ')}</label>
                            <select onchange="ecommerce.catalog.select_variant('${variant.item_code}')">
                                <option value="">Select...</option>
                                ${product.variants.map(v => `
                                    <option value="${v.item_code}">${Object.values(v.attributes).join(', ')}</option>
                                `).join('')}
                            </select>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            variants_container.innerHTML = '';
        }
    }
    
    update_product_specifications(product) {
        const specs_container = document.getElementById('product-specifications');
        
        if (product.website_specifications) {
            const specs = Object.entries(product.website_specifications);
            specs_container.innerHTML = `
                <table class="specifications-table">
                    ${specs.map(([key, value]) => `
                        <tr>
                            <td>${key}</td>
                            <td>${value}</td>
                        </tr>
                    `).join('')}
                </table>
            `;
        } else {
            specs_container.innerHTML = '<p>No specifications available</p>';
        }
    }
    
    async load_product_reviews(product) {
        try {
            const reviews_container = document.getElementById('product-reviews');
            
            if (product.reviews && product.reviews.length > 0) {
                reviews_container.innerHTML = `
                    <div class="reviews-list">
                        ${product.reviews.map(review => `
                            <div class="review">
                                <div class="review-header">
                                    <span class="reviewer">${review.customer_name}</span>
                                    <div class="rating">
                                        ${this.render_stars(review.rating)}
                                    </div>
                                    <span class="date">${this.format_date(review.creation)}</span>
                                </div>
                                <div class="review-title">${review.review_title}</div>
                                <div class="review-content">${review.review_comment}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                reviews_container.innerHTML = '<p>No reviews yet. Be the first to review this product!</p>';
            }
            
        } catch (error) {
            console.error('Error loading reviews:', error);
        }
    }
    
    async load_related_products(product) {
        try {
            const related_container = document.getElementById('related-products-grid');
            
            if (product.related_products && product.related_products.length > 0) {
                related_container.innerHTML = this.components.product_grid.render(product.related_products);
            } else {
                related_container.innerHTML = '<p>No related products found</p>';
            }
            
        } catch (error) {
            console.error('Error loading related products:', error);
        }
    }
    
    render_stars(rating) {
        const full_stars = Math.floor(rating);
        const has_half_star = rating % 1 !== 0;
        
        let stars = '';
        
        for (let i = 0; i < full_stars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        
        if (has_half_star) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        
        const empty_stars = 5 - Math.ceil(rating);
        for (let i = 0; i < empty_stars; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return stars;
    }
    
    format_currency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }
    
    format_date(date_string) {
        return new Date(date_string).toLocaleDateString();
    }
    
    set_loading(loading) {
        this.state.loading = loading;
        
        const loading_indicator = document.getElementById('loading-indicator');
        if (loading_indicator) {
            loading_indicator.style.display = loading ? 'block' : 'none';
        }
    }
    
    handle_error(error) {
        this.state.error = error;
        
        console.error('E-commerce error:', error);
        
        // Show error message to user
        const error_container = document.getElementById('error-message');
        if (error_container) {
            error_container.textContent = error.message || 'An error occurred';
            error_container.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                error_container.style.display = 'none';
            }, 5000);
        }
    }
    
    setup_event_listeners() {
        // Cart events
        document.addEventListener('cart:updated', (event) => {
            this.update_cart_ui(event.detail.cart);
        });
        
        // User events
        document.addEventListener('user:login', (event) => {
            this.state.user = event.detail.user;
            this.update_user_ui();
        });
        
        // Performance monitoring
        window.addEventListener('load', () => {
            this.performance.track_page_load();
        });
    }
    
    update_cart_ui(cart) {
        this.state.cart = cart;
        
        // Update cart count in header
        const cart_count = document.getElementById('cart-count');
        if (cart_count) {
            const total_items = cart.items.reduce((sum, item) => sum + item.qty, 0);
            cart_count.textContent = total_items;
        }
        
        // Update cart sidebar if open
        if (this.components.cart_sidebar.is_open) {
            this.components.cart_sidebar.update_cart(cart);
        }
    }
    
    update_user_ui() {
        const user_menu = document.getElementById('user-menu');
        if (user_menu) {
            user_menu.innerHTML = this.components.user_menu.render(this.state.user);
        }
    }
}

// Product catalog component
class ProductCatalog {
    constructor() {
        this.current_product = null;
        this.current_category = null;
    }
    
    async get_featured_products() {
        const response = await fetch('/api/method/ecommerce.api.get_featured_products');
        const data = await response.json();
        return data.message;
    }
    
    async get_products(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`/api/method/ecommerce.api.get_products?${params}`);
        const data = await response.json();
        return data.message;
    }
    
    async get_categories() {
        const response = await fetch('/api/method/ecommerce.api.get_categories');
        const data = await response.json();
        return data.message;
    }
    
    async get_product_details(product_id) {
        const response = await fetch(`/api/method/ecommerce.api.get_product_details?item_code=${product_id}`);
        const data = await response.json();
        return data.message;
    }
    
    browse_products() {
        ecommerce.router.navigate('/products');
    }
    
    browse_category(category_name) {
        ecommerce.router.navigate(`/category/${encodeURIComponent(category_name)}`);
    }
    
    show_tab(tab_name) {
        // Hide all tabs
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Remove active class from all buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(`${tab_name}-tab`).classList.add('active');
        
        // Add active class to clicked button
        event.target.classList.add('active');
    }
    
    change_main_image(image_src) {
        document.getElementById('main-product-image').src = image_src;
        
        // Update thumbnail active state
        document.querySelectorAll('#thumbnail-images img').forEach(thumb => {
            thumb.classList.remove('active');
            if (thumb.src === image_src) {
                thumb.classList.add('active');
            }
        });
    }
    
    select_variant(item_code) {
        // Load variant details
        this.get_product_details(item_code).then(product => {
            ecommerce.current_product = product;
            ecommerce.load_product_detail(item_code);
        });
    }
}

// Shopping cart component
class ShoppingCart {
    constructor() {
        this.session_id = this.get_or_create_session_id();
        this.current_cart = null;
        this.is_open = false;
    }
    
    get_or_create_session_id() {
        let session_id = localStorage.getItem('cart_session_id');
        if (!session_id) {
            session_id = this.generate_session_id();
            localStorage.setItem('cart_session_id', session_id);
        }
        return session_id;
    }
    
    generate_session_id() {
        return 'cart_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    async get_cart() {
        try {
            const response = await fetch(`/api/method/ecommerce.api.get_cart?session_id=${this.session_id}`);
            const data = await response.json();
            this.current_cart = data.message;
            return this.current_cart;
        } catch (error) {
            console.error('Error getting cart:', error);
            return { items: [], total_amount: 0 };
        }
    }
    
    async add_to_cart(item_code, qty = 1) {
        try {
            const response = await fetch('/api/method/ecommerce.api.add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                },
                body: JSON.stringify({
                    session_id: this.session_id,
                    item_code: item_code,
                    qty: qty
                })
            });
            
            const data = await response.json();
            
            if (data.message) {
                this.current_cart = data.message;
                this.update_cart_ui();
                this.show_notification('Product added to cart', 'success');
            }
            
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.show_notification('Failed to add product to cart', 'error');
        }
    }
    
    async remove_from_cart(item_code) {
        try {
            const response = await fetch('/api/method/ecommerce.api.remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                },
                body: JSON.stringify({
                    session_id: this.session_id,
                    item_code: item_code
                })
            });
            
            const data = await response.json();
            
            if (data.message) {
                this.current_cart = data.message;
                this.update_cart_ui();
            }
            
        } catch (error) {
            console.error('Error removing from cart:', error);
        }
    }
    
    async update_quantity(item_code, qty) {
        try {
            const response = await fetch('/api/method/ecommerce.api.update_cart_quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                },
                body: JSON.stringify({
                    session_id: this.session_id,
                    item_code: item_code,
                    qty: qty
                })
            });
            
            const data = await response.json();
            
            if (data.message) {
                this.current_cart = data.message;
                this.update_cart_ui();
            }
            
        } catch (error) {
            console.error('Error updating cart quantity:', error);
        }
    }
    
    update_cart_ui() {
        // Dispatch cart update event
        document.dispatchEvent(new CustomEvent('cart:updated', {
            detail: { cart: this.current_cart }
        }));
    }
    
    show_notification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    toggle_cart() {
        this.is_open = !this.is_open;
        
        const cart_sidebar = document.getElementById('cart-sidebar');
        if (cart_sidebar) {
            cart_sidebar.classList.toggle('open', this.is_open);
        }
        
        if (this.is_open) {
            this.render_cart();
        }
    }
    
    async render_cart() {
        if (!this.current_cart) {
            await this.get_cart();
        }
        
        const cart_content = document.getElementById('cart-content');
        if (cart_content) {
            if (this.current_cart.items.length === 0) {
                cart_content.innerHTML = `
                    <div class="empty-cart">
                        <p>Your cart is empty</p>
                        <button class="btn btn-primary" onclick="ecommerce.catalog.browse_products()">
                            Continue Shopping
                        </button>
                    </div>
                `;
            } else {
                cart_content.innerHTML = `
                    <div class="cart-items">
                        ${this.current_cart.items.map(item => `
                            <div class="cart-item">
                                <img src="${item.image ? '/files/' + item.image : '/assets/placeholder.png'}" alt="${item.item_name}">
                                <div class="item-details">
                                    <h4>${item.item_name}</h4>
                                    <p>${ecommerce.format_currency(item.rate)}</p>
                                </div>
                                <div class="item-quantity">
                                    <button onclick="ecommerce.cart.decrease_item_quantity('${item.item_code}')">-</button>
                                    <input type="number" value="${item.qty}" min="1" onchange="ecommerce.cart.update_item_quantity('${item.item_code}', this.value)">
                                    <button onclick="ecommerce.cart.increase_item_quantity('${item.item_code}')">+</button>
                                </div>
                                <button class="btn-remove" onclick="ecommerce.cart.remove_from_cart('${item.item_code}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="cart-summary">
                        <div class="summary-row">
                            <span>Subtotal:</span>
                            <span>${ecommerce.format_currency(this.current_cart.subtotal || 0)}</span>
                        </div>
                        <div class="summary-row">
                            <span>Shipping:</span>
                            <span>${ecommerce.format_currency(this.current_cart.shipping_cost || 0)}</span>
                        </div>
                        <div class="summary-row">
                            <span>Tax:</span>
                            <span>${ecommerce.format_currency(this.current_cart.tax_amount || 0)}</span>
                        </div>
                        <div class="summary-row total">
                            <span>Total:</span>
                            <span>${ecommerce.format_currency(this.current_cart.total_amount || 0)}</span>
                        </div>
                    </div>
                    
                    <div class="cart-actions">
                        <button class="btn btn-secondary" onclick="ecommerce.catalog.browse_products()">
                            Continue Shopping
                        </button>
                        <button class="btn btn-primary" onclick="ecommerce.checkout.start_checkout()">
                            Checkout
                        </button>
                    </div>
                `;
            }
        }
    }
    
    decrease_item_quantity(item_code) {
        const current_item = this.current_cart.items.find(item => item.item_code === item_code);
        if (current_item && current_item.qty > 1) {
            this.update_quantity(item_code, current_item.qty - 1);
        }
    }
    
    increase_item_quantity(item_code) {
        const current_item = this.current_cart.items.find(item => item.item_code === item_code);
        if (current_item) {
            this.update_quantity(item_code, current_item.qty + 1);
        }
    }
    
    update_item_quantity(item_code, qty) {
        const quantity = parseInt(qty);
        if (quantity > 0) {
            this.update_quantity(item_code, quantity);
        }
    }
    
    buy_now() {
        // Add current product to cart and go to checkout
        const current_product = ecommerce.current_product;
        if (current_product) {
            this.add_to_cart(current_product.item_code, 1).then(() => {
                ecommerce.checkout.start_checkout();
            });
        }
    }
}

// Initialize e-commerce app
let ecommerce;

document.addEventListener('DOMContentLoaded', () => {
    ecommerce = new EcommerceFrontend();
});
```

### 11.3 Performance Optimization and Analytics

#### High-Performance E-commerce Patterns

```python
# E-commerce performance optimization
class EcommercePerformanceOptimizer:
    def __init__(self):
        self.cache_manager = EcommerceCacheManager()
        self.query_optimizer = EcommerceQueryOptimizer()
        self.image_optimizer = ImageOptimizer()
        self.cdn_manager = CDNManager()
        self.analytics_engine = EcommerceAnalyticsEngine()
    
    def optimize_product_catalog(self):
        """Optimize product catalog performance"""
        # Implement product caching
        self.cache_manager.setup_product_cache()
        
        # Optimize product queries
        self.query_optimizer.optimize_product_queries()
        
        # Optimize images
        self.image_optimizer.optimize_product_images()
        
        # Setup CDN
        self.cdn_manager.setup_product_cdn()
    
    def optimize_checkout_process(self):
        """Optimize checkout performance"""
        # Cache checkout data
        self.cache_manager.setup_checkout_cache()
        
        # Optimize payment processing
        self.optimize_payment_processing()
        
        # Reduce checkout steps
        this.streamline_checkout_flow()
    
    def optimize_search_performance(self):
        """Optimize search performance"""
        # Implement search caching
        self.cache_manager.setup_search_cache()
        
        # Optimize search indexing
        self.query_optimizer.optimize_search_index()
        
        # Implement autocomplete
        this.setup_search_autocomplete()
    
    def track_performance_metrics(self):
        """Track e-commerce performance metrics"""
        metrics = {
            'page_load_time': self.get_page_load_times(),
            'conversion_rate': self.get_conversion_rates(),
            'cart_abandonment_rate': self.get_cart_abandonment_rates(),
            'search_performance': self.get_search_performance(),
            'payment_success_rate': self.get_payment_success_rates()
        }
        
        return metrics

# E-commerce analytics engine
class EcommerceAnalyticsEngine:
    def __init__(self):
        self.tracker = UserBehaviorTracker()
        self.conversion_analyzer = ConversionAnalyzer()
        funnels_analyzer = SalesFunnelAnalyzer()
        self.reporting_engine = EcommerceReportingEngine()
    
    def track_user_behavior(self, user_id, event_data):
        """Track user behavior events"""
        events = [
            'page_view',
            'product_view',
            'search',
            'add_to_cart',
            'remove_from_cart',
            'checkout_start',
            'checkout_complete',
            'purchase'
        ]
        
        if event_data['event'] in events:
            self.tracker.track_event(user_id, event_data)
    
    def analyze_conversion_funnel(self, date_range=None):
        """Analyze conversion funnel"""
        funnel_steps = [
            'visitors',
            'product_views',
            'add_to_cart',
            'checkout_start',
            'checkout_complete',
            'purchase'
        ]
        
        funnel_data = {}
        
        for step in funnel_steps:
            funnel_data[step] = self.get_funnel_step_data(step, date_range)
        
        return self.funnels_analyzer.calculate_funnel_metrics(funnel_data)
    
    def get_product_analytics(self, item_code, date_range=None):
        """Get product-specific analytics"""
        return {
            'views': self.get_product_views(item_code, date_range),
            'add_to_cart_rate': self.get_add_to_cart_rate(item_code, date_range),
            'conversion_rate': self.get_product_conversion_rate(item_code, date_range),
            'revenue': self.get_product_revenue(item_code, date_range),
            'average_rating': self.get_product_average_rating(item_code),
            'review_count': self.get_product_review_count(item_code)
        }
    
    def get_customer_analytics(self, customer_id, date_range=None):
        """Get customer-specific analytics"""
        return {
            'total_orders': self.get_customer_order_count(customer_id, date_range),
            'total_spent': self.get_customer_total_spent(customer_id, date_range),
            'average_order_value': self.get_customer_average_order_value(customer_id, date_range),
            'favorite_products': self.get_customer_favorite_products(customer_id, date_range),
            'purchase_frequency': self.get_customer_purchase_frequency(customer_id, date_range),
            'customer_lifetime_value': self.get_customer_lifetime_value(customer_id)
        }

# Advanced recommendation engine
class RecommendationEngine:
    def __init__(self):
        self.collaborative_filter = CollaborativeFilter()
        self.content_based_filter = ContentBasedFilter()
        self.hybrid_recommender = HybridRecommender()
        self.real_time_recommender = RealTimeRecommender()
    
    def get_product_recommendations(self, user_id, item_code=None, limit=10):
        """Get product recommendations for user"""
        recommendations = []
        
        # Get collaborative filtering recommendations
        cf_recs = self.collaborative_filter.get_recommendations(user_id, limit)
        recommendations.extend(cf_recs)
        
        # Get content-based recommendations if viewing specific product
        if item_code:
            cb_recs = self.content_based_filter.get_similar_products(item_code, limit)
            recommendations.extend(cb_recs)
        
        # Get hybrid recommendations
        hybrid_recs = self.hybrid_recommender.get_recommendations(user_id, item_code, limit)
        recommendations.extend(hybrid_recs)
        
        # Remove duplicates and sort by score
        unique_recs = {}
        for rec in recommendations:
            if rec['item_code'] not in unique_recs or rec['score'] > unique_recs[rec['item_code']]['score']:
                unique_recs[rec['item_code']] = rec
        
        # Sort by score and return top recommendations
        sorted_recs = sorted(unique_recs.values(), key=lambda x: x['score'], reverse=True)
        return sorted_recs[:limit]
    
    def get_personalized_recommendations(self, user_id, context=None):
        """Get personalized recommendations based on user context"""
        # Get real-time recommendations
        real_time_recs = self.real_time_recommender.get_recommendations(user_id, context)
        
        # Get historical recommendations
        historical_recs = self.get_product_recommendations(user_id)
        
        # Combine and weight recommendations
        combined_recs = self.combine_recommendations(real_time_recs, historical_recs)
        
        return combined_recs
    
    def update_recommendation_models(self):
        """Update recommendation models with latest data"""
        # Update collaborative filtering model
        self.collaborative_filter.update_model()
        
        # Update content-based model
        self.content_based_filter.update_model()
        
        # Update hybrid model
        self.hybrid_recommender.update_model()
```

## 🛠️ Practical Exercises

### Exercise 11.1: Build a Complete E-commerce Platform

Create a full e-commerce platform with:
- Product catalog with categories and variants
- Shopping cart with persistent sessions
- Multi-step checkout process
- Payment gateway integration
- Order management system

### Exercise 11.2: Implement Advanced Features

Add advanced e-commerce features:
- Product recommendations engine
- Customer reviews and ratings
- Advanced search with filters
- Wishlist functionality
- Order tracking system

### Exercise 11.3: Optimize for Performance

Implement performance optimizations:
- Product caching strategies
- Image optimization and CDN
- Database query optimization
- Real-time inventory sync
- Analytics and reporting

## 🚀 Best Practices

### E-commerce Architecture

- **Use ERPNext as backend** for inventory, orders, and customer management
- **Implement proper caching** for product data and pricing
- **Design for scalability** with microservices architecture
- **Use responsive design** for mobile-first experience
- **Implement security best practices** for payment processing

### Performance Optimization

- **Cache product data** at multiple levels
- **Optimize images** with proper sizing and compression
- **Use CDN** for static assets
- **Implement lazy loading** for product images
- **Monitor performance** with real-time analytics

### User Experience

- **Simplify checkout process** with minimal steps
- **Provide clear product information** with high-quality images
- **Implement intuitive search** with autocomplete
- **Offer multiple payment options**
- **Ensure mobile responsiveness** across all devices

## 📖 Further Reading

- [ERPNext E-commerce Documentation](https://erpnext.com/docs/user/en/ecommerce)
- [E-commerce Performance Optimization](https://developers.google.com/web/fundamentals/performance/)
- [Payment Gateway Integration](https://stripe.com/docs)
- [E-commerce Analytics](https://www.google-analytics.com/solutions/ecommerce)

## 🎯 Chapter Summary

Building a complete e-commerce platform requires:

- **Platform Architecture** provides the foundation for scalable online stores
- **Product Catalog Management** enables effective product presentation
- **Shopping Cart & Checkout** creates seamless purchasing experience
- **Payment Processing** ensures secure and reliable transactions
- **Performance Optimization** delivers fast and responsive user experience

---

**Next Chapter**: CRM system development with customer relationship management automation.
