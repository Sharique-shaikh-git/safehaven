# Sample pipeline run (proof)

Run command:
```bash
uv run -m agents.orchestrator
```

Output:

Microsoft Windows [Version 10.0.19045.6466]
(c) Microsoft Corporation. All rights reserved.

D:\project\safehaven-starter\safehaven>d:\project\safehaven-starter\safehaven\.venv\Scripts\activate.bat

(safehaven) D:\project\safehaven-starter\safehaven>uv run -m agents.orchestrator
SafeHaven Pipeline — End-to-End Test
Report: Flooding on Main Street, water rising fast, about 15 people stuck on rooftops, need rescue and medical help urgently


============================================================
STAGE 1 — INTAKE AGENT
============================================================
```json
{
  "report_id": "a1b2c3d4",
  "location_text": "Main Street",
  "lat": null,
  "lon": null,
  "disaster_type": "Flooding",
  "people_affected": 15,
  "needs": ["rescue", "medical", "shelter"],
  "redacted_summary": "Flooding on Main Street, water rising fast. Approximately 15 people are stuck on rooftops and urgently need rescue and medical help.",
  "raw_pii": {
    "names": [],
    "phones": []
  }
}
```

============================================================
STAGE 2 — CRISIS ASSESSOR AGENT
============================================================
```json
{
  "report_id": "a1b2c3d4",
  "original_severity": 8,
  "assessed_severity": 9,
  "severity_label": "Critical",
  "escalate_immediately": true,
  "weather_summary": "Weather data unavailable due to missing latitude and longitude coordinates in the report. Cannot assess current weather conditions.",
  "secondary_risks": [
    "Ongoing flooding and water spread",
    "Waterborne disease outbreak",
    "Structural damage or collapse of buildings where people are trapped",
    "Hypothermia risk for exposed individuals"
  ],
  "risk_justification": "The original report highlights a critical situation: 15 individuals are trapped on rooftops with water rising fast, urgently requiring rescue and medical assistance. This presents an immediate and severe life threat to multiple people, warranting an upgrade to a Critical severity. Weather data could not be obtained due to missing location coordinates. Key secondary risks include the continued spread of floodwaters, potential structural integrity issues for affected buildings, waterborne disease, and hypothermia for those exposed on rooftops.",
  "recommended_priority": "mass_casualty"
}
```

→ Extracted assessed_severity: 9

============================================================
STAGE 3 — PARALLEL BRANCH TRIGGERED (severity=9 > 5)
  resource_allocator + volunteer_coordinator running concurrently
============================================================
Node execution failed with exception
Traceback (most recent call last):
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 135, in run
    await self._execute_node(ctx, node_input)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 255, in _execute_node
    await self._run_node_loop(ctx, node_input)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 269, in _run_node_loop
    async for event in agen:
      self._track_event_in_context(event, ctx)
      await self._enqueue_event(event, ctx)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_base_node.py", line 217, in run
    async for item in agen:
    ...<12 lines>...
        yield Event(output=validated)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\agents\llm_agent.py", line 559, in _run_impl
    async for event in agen:
    ...<4 lines>...
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_llm_agent_wrapper.py", line 383, in run_llm_agent_as_node
    async for event in run_iter:
    ...<22 lines>...
          break
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\agents\base_agent.py", line 305, in run_async
    async for event in agen:
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\agents\llm_agent.py", line 515, in _run_async_impl
    async for event in agen:
    ...<5 lines>...
        should_pause = True
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 889, in run_async
    async for event in agen:
      last_event = event
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 968, in _run_one_step_async
    async for llm_response in agen:
    ...<13 lines>...
          yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 1362, in _call_llm_async
    async for event in agen:
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 1340, in _call_llm_with_tracing
    async for llm_response in agen:
    ...<18 lines>...
      yield llm_response
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 1423, in _run_and_handle_error
    async for response in agen:
      yield response
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 408, in _run_and_handle_error
    raise model_error
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 385, in _run_and_handle_error
    async for llm_response in agen:
      tel_ctx.record_llm_response(invocation_context, llm_response)
      yield llm_response
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\models\google_llm.py", line 274, in generate_content_async
    response = await self.api_client.aio.models.generate_content(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\models.py", line 8669, in generate_content
    response = await self._generate_content(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        model=model, contents=contents, config=final_parsed_config_to_call
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\models.py", line 7115, in _generate_content
    response = await self._api_client.async_request(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        'post', path, request_dict, http_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\_api_client.py", line 1664, in async_request
    result = await self._async_request(
             ^^^^^^^^^^^^^^^^^^^^^^^^^
        http_request=http_request, http_options=http_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\_api_client.py", line 1597, in _async_request
    return await self._async_retry(  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self._async_request_once, http_request, stream
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\tenacity\asyncio\__init__.py", line 112, in __call__
    do = await self.iter(retry_state=retry_state)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\tenacity\asyncio\__init__.py", line 157, in iter
    result = await action(retry_state)
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\tenacity\_utils.py", line 111, in inner
    return call(*args, **kwargs)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\tenacity\__init__.py", line 413, in exc_check
    raise retry_exc.reraise()
          ~~~~~~~~~~~~~~~~~^^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\tenacity\__init__.py", line 184, in reraise
    raise self.last_attempt.result()
          ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\hp\AppData\Local\Programs\Python\Python313\Lib\concurrent\futures\_base.py", line 449, in result
    return self.__get_result()
           ~~~~~~~~~~~~~~~~~^^
  File "C:\Users\hp\AppData\Local\Programs\Python\Python313\Lib\concurrent\futures\_base.py", line 401, in __get_result
    raise self._exception
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\tenacity\asyncio\__init__.py", line 116, in __call__
    result = await fn(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\_api_client.py", line 1577, in _async_request_once
    await errors.APIError.raise_for_async_response(client_response)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\errors.py", line 247, in raise_for_async_response
    await cls.raise_error_async(status_code, response_json, response)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\errors.py", line 271, in raise_error_async
    raise ServerError(status_code, response_json, response)
google.genai.errors.ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}

Root node volunteer_coordinator failed.
Traceback (most recent call last):
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\runners.py", line 815, in _cleanup_root_task
    await task
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\runners.py", line 560, in _drive_root_node
    raise ctx.error
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 135, in run
    await self._execute_node(ctx, node_input)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 255, in _execute_node
    await self._run_node_loop(ctx, node_input)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 269, in _run_node_loop
    async for event in agen:
      self._track_event_in_context(event, ctx)
      await self._enqueue_event(event, ctx)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_base_node.py", line 217, in run
    async for item in agen:
    ...<12 lines>...
        yield Event(output=validated)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\agents\llm_agent.py", line 559, in _run_impl
    async for event in agen:
    ...<4 lines>...
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_llm_agent_wrapper.py", line 383, in run_llm_agent_as_node
    async for event in run_iter:
    ...<22 lines>...
          break
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\agents\base_agent.py", line 305, in run_async
    async for event in agen:
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\agents\llm_agent.py", line 515, in _run_async_impl
    async for event in agen:
    ...<5 lines>...
        should_pause = True
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 889, in run_async
    async for event in agen:
      last_event = event
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 968, in _run_one_step_async
    async for llm_response in agen:
    ...<13 lines>...
          yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 1362, in _call_llm_async
    async for event in agen:
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 1340, in _call_llm_with_tracing
    async for llm_response in agen:
    ...<18 lines>...
      yield llm_response
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 1423, in _run_and_handle_error
    async for response in agen:
      yield response
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 408, in _run_and_handle_error
    raise model_error
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\flows\llm_flows\base_llm_flow.py", line 385, in _run_and_handle_error
    async for llm_response in agen:
      tel_ctx.record_llm_response(invocation_context, llm_response)
      yield llm_response
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\models\google_llm.py", line 274, in generate_content_async
    response = await self.api_client.aio.models.generate_content(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\models.py", line 8669, in generate_content
    response = await self._generate_content(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        model=model, contents=contents, config=final_parsed_config_to_call
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\models.py", line 7115, in _generate_content
    response = await self._api_client.async_request(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        'post', path, request_dict, http_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\_api_client.py", line 1664, in async_request
    result = await self._async_request(
             ^^^^^^^^^^^^^^^^^^^^^^^^^
        http_request=http_request, http_options=http_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\genai\_api_client.py", line 1597, in _async_request
    return await self._async_retry(  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ... (omitted for brevity in this markdown snapshot) ...

google.genai.errors.ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}

Root node resource_allocator was cancelled.
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "D:\project\safehaven-starter\safehaven\agents\orchestrator.py", line 280, in <module>
    asyncio.run(run_pipeline(SAMPLE_REPORT))
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "C:\Users\hp\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "C:\Users\hp\AppData\Local\Programs\Python\Python313\Lib\asyncio\base_events.py", line 725, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "D:\project\safehaven-starter\safehaven\agents\orchestrator.py", line 206, in run_pipeline
    allocator_output, coordinator_output = await asyncio.gather(
                                           ^^^^^^^^^^^^^^^^^^^^^
        run_allocator(), run_coordinator()
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\project\safehaven-starter\safehaven\agents\orchestrator.py", line 196, in run_coordinator
    return await _run_agent(
           ^^^^^^^^^^^^^^^^^
    ...<7 lines>...
    )
    ^
  File "D:\project\safehaven-starter\safehaven\agents\orchestrator.py", line 78, in _run_agent
    async for event in runner.run_async(
    ...<7 lines>...
                    final_text = part.text
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\runners.py", line 1017, in run_async
    async for event in agen:
      yield event
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\runners.py", line 574, in _run_node_async
    await self._cleanup_root_task(task, self.agent.name)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\runners.py", line 815, in _cleanup_root_task
    await task
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\runners.py", line 560, in _drive_root_node
    raise ctx.error
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 135, in run
    await self._execute_node(ctx, node_input)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 255, in _execute_node
    await self._run_node_loop(ctx, node_input)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_node_runner.py", line 269, in _run_node_loop
    async for event in agen:
      self._track_event_in_context(event, ctx)
      await self._enqueue_event(event, ctx)
  File "D:\project\safehaven-starter\safehaven\.venv\Lib\site-packages\google\adk\workflow\_base_node.py", line 217, in run
    async for item in agen:
    ... (stack continues) ...

google.genai.errors.ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
