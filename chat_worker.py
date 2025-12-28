import asyncio
import json
import socket

import redis.exceptions

from app.infra.redis_client import get_redis, STREAM_NAME, GROUP_NAME
from app.services.vllm import call_vllm

CONSUMER_NAME = socket.gethostname()


async def worker_loop():
    print(f"🟢 GPU worker started: {CONSUMER_NAME}")

    redis_client = get_redis()

    while True:
        try:
            response = await redis_client.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={STREAM_NAME: ">"},
                count=1,
                block=1000,   # short block avoids TLS hangs
            )

            if not response:
                continue

            for _, messages in response:
                for message_id, fields in messages:
                    job_id = fields["job_id"]

                    try:
                        print(f"📥 Processing job {job_id}")

                        payload = json.loads(fields["payload"])
                        result = await call_vllm(payload)

                        await redis_client.set(
                            f"chat:result:{job_id}",
                            json.dumps(result),
                            ex=3600,
                        )

                        await redis_client.xack(
                            STREAM_NAME,
                            GROUP_NAME,
                            message_id,
                        )

                        print(f"✅ Finished job {job_id}")

                    except Exception as e:
                        print(f"❌ Job {job_id} failed:", e)
                        # Not acked → stays pending

        except (asyncio.TimeoutError, redis.exceptions.TimeoutError):
            print("⚠️ Redis timeout — reconnecting")
            await redis_client.close()
            redis_client = get_redis()
            await asyncio.sleep(0.5)

        except Exception as e:
            print("🔥 Fatal Redis error:", e)
            await redis_client.close()
            redis_client = get_redis()
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(worker_loop())
