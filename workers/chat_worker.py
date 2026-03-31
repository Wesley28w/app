from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/workspace/.env", override=True)

import asyncio
import json
import socket
from redis.exceptions import TimeoutError

from app.infra.redis_client import (
    redis_client,
    STREAM_NAME,
    GROUP_NAME,
)
from app.services.vllm import chat_with_vllm

CONSUMER_NAME = socket.gethostname()


async def worker_loop():
    print(f"🟢 GPU worker started: {CONSUMER_NAME}")

    while True:
        pending = await redis_client.xpending_range(
            STREAM_NAME,
            GROUP_NAME,
            min="-",
            max="+",
            count=10,
        )
    
        for p in pending:
            if p.get("idle", 0) > 30000:
                await redis_client.xclaim(
                    STREAM_NAME,
                    GROUP_NAME,
                    CONSUMER_NAME,
                    min_idle_time=30000,
                    message_ids=[p["message_id"]],
            )
        
        try:
            response = await redis_client.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={STREAM_NAME: ">"},
                count=1,
                block=5000,  # block for 5s waiting for work
            )

            if not response:
                continue

            for _, messages in response:
                for message_id, fields in messages:
                    try:
                        payload = json.loads(fields["payload"])
                        job_id = fields["job_id"]

                        result = await chat_with_vllm(payload)

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

                    except Exception as e:
                        print("❌ Job failed:", e)
                        # Leave unacked → retried later

        except TimeoutError:
            # ⏱️ Normal when Redis has no messages
            continue

        except Exception as e:
            print("🔥 Worker loop error:", e)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(worker_loop())
