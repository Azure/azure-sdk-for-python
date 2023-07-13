# The MIT License (MIT)
# Copyright (c) 2022 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

async def heap_push(heap, item, document_producer_comparator):
    """Push item onto heap, maintaining the heap invariant.
    :param list heap:
    :param Any item:
    :param _PartitionKeyRangeDocumentProducerComparator document_producer_comparator:
    """
    heap.append(item)
    await _sift_down(heap, document_producer_comparator, 0, len(heap) - 1)


async def heap_pop(heap, document_producer_comparator):
    """Pop the smallest item off the heap, maintaining the heap invariant.
    :param list heap: the heap to use for comparing
    :param _PartitionKeyRangeDocumentProducerComparator document_producer_comparator: the document producer comparator
    :returns: the popped item from the heap
    :rtype: Any
    """
    last_elt = heap.pop()  # raises appropriate IndexError if heap is empty
    if heap:
        return_item = heap[0]
        heap[0] = last_elt
        await _sift_up(heap, document_producer_comparator, 0)
        return return_item
    return last_elt


async def _sift_down(heap, document_producer_comparator, start_pos, pos):
    new_item = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # new_item fits.
    while pos > start_pos:
        parent_pos = (pos - 1) >> 1
        parent = heap[parent_pos]
        if await document_producer_comparator.compare(new_item, parent) < 0:
            # if new_item < parent:
            heap[pos] = parent
            pos = parent_pos
            continue
        break
    heap[pos] = new_item


async def _sift_up(heap, document_producer_comparator, pos):
    end_pos = len(heap)
    start_pos = pos
    new_item = heap[pos]
    # Bubble up the smaller child until hitting a leaf.
    child_pos = 2 * pos + 1  # leftmost child position
    while child_pos < end_pos:
        # Set child_pos to index of smaller child.
        right_pos = child_pos + 1
        # if right_pos < end_pos and not heap[child_pos] < heap[right_pos]:
        if right_pos < end_pos and not await document_producer_comparator.compare(heap[child_pos], heap[right_pos]) < 0:
            child_pos = right_pos
        # Move the smaller child up.
        heap[pos] = heap[child_pos]
        pos = child_pos
        child_pos = 2 * pos + 1
    # The leaf at pos is empty now.  Put new_item there, and bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = new_item
    await _sift_down(heap, document_producer_comparator, start_pos, pos)
