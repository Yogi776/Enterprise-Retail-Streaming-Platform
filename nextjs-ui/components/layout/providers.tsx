"use client";

import { ApolloProvider } from "@apollo/client";
import apolloClient from "@/lib/graphql/client";
import { RealtimeProvider } from "@/hooks/use-realtime";

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ApolloProvider client={apolloClient}>
      <RealtimeProvider>
        {children}
      </RealtimeProvider>
    </ApolloProvider>
  );
}