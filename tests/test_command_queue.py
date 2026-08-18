from heat_pump_modbus_service.command_queue import CommandQueue


def test_mqtt_callback_only_queues_command_until_main_loop_drains_it():
    handled = []
    queue = CommandQueue(lambda topic, payload: handled.append((topic, payload)))

    queue.enqueue("heat_pump/utility_room/operation_mode/set", b"heat")

    assert handled == []
    assert queue.drain() == 1
    assert handled == [("heat_pump/utility_room/operation_mode/set", b"heat")]


def test_command_queue_wakes_main_loop_when_message_arrives():
    queue = CommandQueue(lambda _topic, _payload: None)

    assert not queue.wait_for_work(0)
    queue.enqueue("heat_pump/utility_room/quiet_mode/set", b"on")

    assert queue.wait_for_work(0)
