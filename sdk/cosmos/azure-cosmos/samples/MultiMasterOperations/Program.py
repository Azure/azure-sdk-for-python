from MultiMasterScenario import MultiMasterScenario

if __name__ == '__main__':
    print("Multimaster demo started!")
    scenario = MultiMasterScenario()
    scenario.initialize_async()
    scenario.run_basic_async()
    scenario.run_manual_conflict_async()
    scenario.run_LWW_async()
    scenario.run_UDP_async()
