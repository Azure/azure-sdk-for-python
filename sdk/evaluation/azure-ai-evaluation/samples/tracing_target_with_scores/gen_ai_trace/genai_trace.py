import json
import time
import uuid
from functools import wraps

def gen_ai_trace(tracer, name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name=name) as span:
                result = func(*args, **kwargs)
                span.set_attribute("gen_ai.system", name)
                span.set_attribute("gen_ai.operation.name", "chat")
                span.set_attribute("gen_ai.request.model", "gpt-4")

                for key, value in kwargs.items():
                    span.add_event(
                        name="gen_ai.user.message",
                        attributes={
                            "gen_ai.system": name,
                            "gen_ai.event.content": json.dumps({"role": key, "content": value}),
                        },
                    )

                span.add_event(
                    name="gen_ai.choice",
                    attributes={
                        "gen_ai.event.content": json.dumps({"message": {"content": result["response"]}}),
                        "gen_ai.response.id": result["metadata"]["response_id"],
                    },
                )

            return result
        return wrapper
    return decorator
