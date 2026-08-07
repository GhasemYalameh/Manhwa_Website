const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost";

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown, message?: string) {
    super(message ?? `درخواست با کد ${status} ناموفق بود`);
    this.status = status;
    this.body = body;
  }
}

export async function apiPost<TResponse>(
  path: string,
  body: unknown,
  accessToken?: string
): Promise<TResponse> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `JWT ${accessToken}` } : {}),
    },
    body: JSON.stringify(body),
  });

  const isJson = res.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await res.json() : null;

  if (!res.ok) {
    throw new ApiError(res.status, data);
  }

  return data as TResponse;
}
