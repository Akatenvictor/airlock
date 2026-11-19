import { NextResponse } from "next/server";
import { PROPOSALS_TTL_MS, getCachedProposals } from "@/lib/proposals-cache";

/**
 * JSON list of proposals for client-side readers, such as the notification
 * center (issue #278). The data layer runs on the server only, so this route is
 * how a browser component reads the same list the pages render.
 *
 * Every open notification center polls this route, so it must not cost one RPC
 * read per request. The list is shared from `getCachedProposals()`, read at
 * most once per PROPOSALS_TTL_MS however many visitors are polling, and the
 * response may be reused by a CDN or proxy for the same window. A status change
 * still appears within that window.
 *
 * Kept dynamic so the list is never frozen into the build.
 */
export const dynamic = "force-dynamic";

const TTL_SECONDS = Math.round(PROPOSALS_TTL_MS / 1000);

export async function GET(): Promise<Response> {
  try {
    return NextResponse.json(await getCachedProposals(), {
      headers: {
        "Cache-Control": `public, max-age=0, s-maxage=${TTL_SECONDS}, stale-while-revalidate=${TTL_SECONDS * 2}`,
      },
    });
  } catch {
    return NextResponse.json(
      { error: "Proposals are unavailable" },
      { status: 500, headers: { "Cache-Control": "no-store" } },
    );
  }
}
