import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const handler = NextAuth({
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user }) {
      return user.email?.endsWith("@monstar-lab.com") ?? false;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login",
  },
  cookies: {
    state: {
      name: "next-auth.state",
      options: {
        httpOnly: true,
        sameSite: "lax" as const,
        path: "/",
        secure: true,
      },
    },
  },
});

export { handler as GET, handler as POST };
