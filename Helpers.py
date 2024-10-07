import random
from typing import TypeVar
import pprint
import textwrap

def long_print(text_to_print): print(textwrap.dedent(text_to_print).strip())

def log_time_info(time_logs: list[tuple[str, float, float]], student_count: int) -> None:
    def formatted_time(time: float) -> str:
        if time >= 3600:
            return f"{time / 3600:.2f} hours"
        elif time >= 60:
            return f"{time / 60:.2f} minutes"
        elif time >= 1:
            return f"{time:.2f} seconds"
        elif time >= 0.001:
            return f"{time * 1000:.2f} milliseconds"
        elif time >= 0.000001:
            return f"{time * 1000000:.2f} microseconds"
        else:
            return f"{time * 1000000000:.2f} nanoseconds"

    total_time = sum(time_taken for _, _, time_taken in time_logs)
    if total_time / 2 == time_logs[-1][2]: # If last row is a total row
        total_time -= time_logs[-1][2]
        time_logs = time_logs[:-1]
    
    titles = [
        (
            f"   {' ' * (2 - len(str(round((time / total_time) * 100))))}{(time / total_time) * 100:.0f}% {log}", 
            time, 
            time / total_time
        ) for log, _, time in time_logs
    ]
    titles.sort(key=lambda title: title[2], reverse=True)
    max_title_len = max(len(title) for title, _, _ in titles)

    print("\n---------------------------------------")
    print(f"T I M I N G   L O G S :")
    for title, time, _ in titles: print(f"{title}{" " * (max_title_len - len(title))}  {formatted_time(time)}")
    print(f"\nTook {formatted_time(total_time)} for {student_count} entries\nfor an average time of {formatted_time(total_time / student_count)}")
    print("---------------------------------------\n")

T = TypeVar("T")

def rand_pop(list: list[T]) -> T:
    list.remove(x:= random.choice(list))
    return x

def rand_n_samples(original_list:list[T], n: int) -> list[list[T]]:
    if n > len(original_list):
        raise ValueError("Number of sublists cannot exceed the length of the original list.")
        
    # Shuffle the list to randomize element order
    random.shuffle(original_list)
    
    # Initialize variables
    remaining_elements = original_list[:]
    result = []
    
    # Distribute elements randomly among the specified number of sublists
    for i in range(n):
        if i == n - 1: result.append(remaining_elements) # The last sublist gets all the remaining elements
        
        else:
            # Calculate the max possible length for this sublist
            max_length = len(remaining_elements) - (n - len(result) - 1)
            sample_length = random.randint(1, max_length)
            
            # Get a random sample of the determined length
            result.append(remaining_elements[:sample_length])
            
            # Remove the sampled elements from the remaining list
            remaining_elements = remaining_elements[sample_length:]
    
    return result

def rand_samples(elements: list[T]) -> list[list[T]]:
    random.shuffle(elements)
    sub_lists: list[list[T]] = []

    while len(elements) > 0:
        sub_lists.append(elements[:(index:=random.randint(1, len(elements)))])
        elements = elements[index:]

    return sub_lists

def remove_all(list: list[T], removing: list[T]):
    for to_remove in removing: list.remove(to_remove)