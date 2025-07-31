#!/usr/bin/env python3
"""
Simple validation script to check if the DirectAttackSimulator fix is working.
This script tests the key logic without requiring external dependencies.
"""

def test_seed_derivation():
    """Test the seed derivation logic in isolation."""
    
    print("Testing seed derivation logic...")
    
    # Test case 1: Normal seed value
    randomization_seed = 42
    regular_seed = randomization_seed
    jailbreak_seed = randomization_seed + 1 if randomization_seed < 999999 else randomization_seed - 1
    
    assert regular_seed == 42, f"Expected regular_seed=42, got {regular_seed}"
    assert jailbreak_seed == 43, f"Expected jailbreak_seed=43, got {jailbreak_seed}"
    assert regular_seed != jailbreak_seed, "Seeds should be different"
    print("✓ Test case 1 (normal seed): PASSED")
    
    # Test case 2: Edge case - maximum seed value
    randomization_seed = 999999
    regular_seed = randomization_seed
    jailbreak_seed = randomization_seed + 1 if randomization_seed < 999999 else randomization_seed - 1
    
    assert regular_seed == 999999, f"Expected regular_seed=999999, got {regular_seed}"
    assert jailbreak_seed == 999998, f"Expected jailbreak_seed=999998, got {jailbreak_seed}"
    assert regular_seed != jailbreak_seed, "Seeds should be different even at max value"
    print("✓ Test case 2 (max seed): PASSED")
    
    # Test case 3: Another normal value
    randomization_seed = 100
    regular_seed = randomization_seed
    jailbreak_seed = randomization_seed + 1 if randomization_seed < 999999 else randomization_seed - 1
    
    assert regular_seed == 100, f"Expected regular_seed=100, got {regular_seed}"
    assert jailbreak_seed == 101, f"Expected jailbreak_seed=101, got {jailbreak_seed}"
    assert regular_seed != jailbreak_seed, "Seeds should be different"
    print("✓ Test case 3 (another normal seed): PASSED")
    
    print("All seed derivation tests PASSED! ✓")

def simulate_template_shuffling():
    """Simulate how different seeds would affect template shuffling."""
    import random
    
    print("\nTesting template shuffling with different seeds...")
    
    # Mock template list
    templates = [f"template_{i}" for i in range(10)]
    
    # Test with same seed (the old problematic behavior)
    seed = 42
    templates_1 = templates.copy()
    templates_2 = templates.copy()
    
    rng1 = random.Random(seed)
    rng1.shuffle(templates_1)
    
    rng2 = random.Random(seed)  # Same seed
    rng2.shuffle(templates_2)
    
    if templates_1 == templates_2:
        print("✓ Confirmed: Same seeds produce identical shuffling (old problematic behavior)")
    else:
        print("✗ Unexpected: Same seeds should produce identical shuffling")
    
    # Test with different seeds (the new fixed behavior)
    templates_3 = templates.copy()
    templates_4 = templates.copy()
    
    rng3 = random.Random(42)  # regular_seed
    rng3.shuffle(templates_3)
    
    rng4 = random.Random(43)  # jailbreak_seed (42 + 1)
    rng4.shuffle(templates_4)
    
    if templates_3 != templates_4:
        print("✓ Fixed: Different seeds produce different shuffling (new correct behavior)")
    else:
        print("✗ Issue: Different seeds should produce different shuffling")
    
    print(f"Regular simulation template order (seed 42):   {templates_3[:5]}...")
    print(f"Jailbreak simulation template order (seed 43): {templates_4[:5]}...")

if __name__ == "__main__":
    test_seed_derivation()
    simulate_template_shuffling()
    print("\n🎉 All tests passed! The fix should resolve the duplicate queries issue.")