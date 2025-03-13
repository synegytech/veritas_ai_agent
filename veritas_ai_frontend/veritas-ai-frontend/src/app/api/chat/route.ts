import { NextResponse } from "next/server";
import { BackendPromptRequest } from "@/types";

export async function POST(request: Request) {
  try {
    // Get the request body
    const body: BackendPromptRequest = await request.json();

    // Forward the request to the Django backend
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/generate/`;

    const response = await fetch(backendUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    // Get the response data
    const data = await response.json();

    // Return the response
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error in chat API route:", error);
    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 }
    );
  }
}
