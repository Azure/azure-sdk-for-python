import re

# The old 2-line pattern
old_lines = '''        :keyword dict[str, Any] availability_strategy:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.'''

# The new enhanced docstring
new_lines = '''        :keyword dict[str, Any] availability_strategy:
            The threshold-based availability strategy configuration for cross-region hedging.
            This dictionary accepts the following keys: ``threshold`` (int) is the initial wait time
            in milliseconds before sending the first hedged request to an alternate region, and
            ``threshold_step`` (int) is the fixed wait time interval in milliseconds between subsequent
            hedged requests. If not provided, the client's default strategy will be used.
            For more information, see:
            https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/README.md#cross-region-hedging-availability-strategy'''

# Process container.py
with open('azure/cosmos/container.py', 'r', encoding='utf-8') as f:
    content = f.read()

count = content.count(old_lines)
print(f'container.py: Found {count} occurrences to replace')

new_content = content.replace(old_lines, new_lines)
with open('azure/cosmos/container.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

# Process aio/_container.py
with open('azure/cosmos/aio/_container.py', 'r', encoding='utf-8') as f:
    content = f.read()

count = content.count(old_lines)
print(f'aio/_container.py: Found {count} occurrences to replace')

new_content = content.replace(old_lines, new_lines)
with open('azure/cosmos/aio/_container.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done!')
