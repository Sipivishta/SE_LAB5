import json
import logging
from typing import List, Union

# --- Configuration ---
# Setting level to INFO to capture all transactions
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

INVENTORY_FILE = "inventory.json"
# Global variable (Necessary for the original function-based structure)
stock_data = {}

def load_data(file_path: str = INVENTORY_FILE):
    """
    Loads inventory data from the JSON file. 
    Initializes empty data if the file is not found or is corrupt.
    
    Args:
        file_path (str): The path to the inventory JSON file.
    """
    global stock_data
    
    try:
        with open(file_path, "r", encoding='utf-8') as file_obj:
            stock_data = json.load(file_obj)
        logging.info(f"Successfully loaded data from {file_path}")
        
    except FileNotFoundError:
        logging.info(f"Inventory file '{file_path}' not found. Starting new inventory.")
        stock_data = {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from '{file_path}'. File corrupt. Starting new inventory.")
        stock_data = {}
    except Exception as err:
        logging.error(
            f"An unexpected error occurred during data loading: {err}", 
            exc_info=True
        )
        stock_data = {}

def save_data(file_path: str = INVENTORY_FILE):
    """
    Saves the current inventory data to the JSON file.

    Args:
        file_path (str): The path to the inventory JSON file.
    """
    try:
        with open(file_path, "w", encoding='utf-8') as file_obj:
            json.dump(stock_data, file_obj, indent=4)
        logging.info(f"Successfully saved data to {file_path}")
        
    except Exception as err:
        logging.error(f"An unexpected error occurred during data saving: {err}", exc_info=True)

def add_item(item: str = "default", qty: Union[int, str] = 0):
    """
    Adds a quantity of an item to the stock, handling validation and negative input.
    
    Args:
        item (str): The name of the item.
        qty (Union[int, str]): The quantity to add.
    """
    if not isinstance(item, str) or not item:
        logging.warning("Invalid item type or empty item name. Skipping.")
        return

    try:
        qty_int = int(qty)
    except (TypeError, ValueError):
        logging.error(f"Invalid quantity type for '{item}': {qty}. Must be integer. Skipping.")
        return

    if qty_int < 0:
        logging.info(f"Negative quantity for {item}. Delegating to remove_item: {abs(qty_int)}")
        remove_item(item, abs(qty_int))
        return
    
    if qty_int == 0:
        logging.debug(f"Attempted to add 0 of {item}.")
        return

    stock_data[item] = stock_data.get(item, 0) + qty_int
    logging.info(f"Added {qty_int} of {item}. New stock: {stock_data[item]}")

def remove_item(item: str, qty: Union[int, str]):
    """
    Removes a quantity of an item, preventing negative stock levels.
    
    Args:
        item (str): The name of the item.
        qty (Union[int, str]): The quantity to remove.
    """
    if not isinstance(item, str) or not item:
        logging.warning("Invalid item type or empty item name. Skipping.")
        return
    
    try:
        qty_int = int(qty)
        if qty_int <= 0:
            logging.warning(f"remove_item called with non-positive quantity: {qty_int}. Ignoring.")
            return
    except (TypeError, ValueError):
        logging.error(f"Invalid quantity type for '{item}': {qty}. Must be integer. Skipping.")
        return
            
    try:
        current_qty = stock_data[item]
        
        # Ensure we only remove what is available (non-negative stock policy)
        qty_removed = min(qty_int, current_qty)
        
        if qty_removed < qty_int:
            logging.warning(
                f"Only {current_qty} of {item} in stock. Removing all available ({qty_removed})."
            )

        stock_data[item] -= qty_removed
        
        if stock_data[item] == 0:
            del stock_data[item]
            logging.info(f"Removed {item} from inventory. Stock depleted.")
        else:
            logging.info(f"Removed {qty_removed} of {item}. Remaining stock: {stock_data[item]}")

    except KeyError:
        logging.error(f"Item '{item}' not found in inventory. Cannot remove.")
    except Exception as err:
        logging.error(f"Unexpected error during item removal: {err}")

def get_qty(item: str) -> int:
    """
    Returns the quantity of a specific item, or 0 if not found.
    
    Args:
        item (str): The name of the item.

    Returns:
        int: The current stock quantity.
    """
    return stock_data.get(item, 0)

def print_data():
    """Prints a formatted report of all items and their quantities to the console."""
    if not stock_data:
        print("\n--- Items Report ---")
        print("Inventory is empty.")
        return

    print("\n--- Items Report ---")
    max_len = max((len(i) for i in stock_data), default=0)
    for item, qty in sorted(stock_data.items()):
        print(f"{item.ljust(max_len)} -> {qty}")
    print("--------------------")

def check_low_items(threshold: int = 5) -> List[str]:
    """
    Returns a list of items whose stock is below the specified threshold.

    Args:
        threshold (int): The stock level below which an item is considered low.

    Returns:
        List[str]: A list of item names that are low in stock.
    """
    return [item for item, qty in stock_data.items() if qty < threshold]

def main():
    """Main execution function to demonstrate inventory operations and persistence."""
    print("--- Inventory System Initializing ---")
    
    load_data()
    
    print("\n--- Starting Inventory Operations ---")

    add_item("apple", 10)
    add_item("banana", 8)
    add_item("orange", 5)
    add_item("grape", "7") 
    
    remove_item("apple", 3)
    add_item("banana", -2) # Removes 2 bananas
    
    # Testing error cases
    add_item(123, "ten")  # Invalid types (logs error)
    remove_item("kiwi", 1) # Non-existent item (logs error)
    remove_item("orange", 10) # Attempts to remove more than stock (logs warning, stock goes to 0)
    
    print("\n--- Reporting ---")
    print(f"Apple stock: {get_qty('apple')}")     # 7
    print(f"Banana stock: {get_qty('banana')}")   # 6
    print(f"Low items (threshold 5): {check_low_items()}") # Should list items < 5
    
    save_data()
    
    # Demonstrate saving and reloading
    global stock_data
    stock_data = {} 
    load_data() 
    
    print_data()
    
    print("\nSecurity risk 'eval' removed.")

if __name__ == "__main__":
    main()