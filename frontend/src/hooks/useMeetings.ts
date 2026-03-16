"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { meetings as meetingsApi, calendar as calendarApi } from "@/lib/api";
import type { Meeting } from "@/types/meeting";

export function useMeetings(params?: { status?: string; search?: string; limit?: number; offset?: number }) {
  const { data: meetings = [], isLoading, error, refetch } = useQuery({
    queryKey: ["meetings", params],
    queryFn: () => meetingsApi.list(params),
  });
  return { meetings, isLoading, error, refetch };
}

export function useMeeting(id: string | number) {
  const numId = typeof id === "string" ? parseInt(id, 10) : id;
  const { data: meeting, isLoading, error, refetch } = useQuery({
    queryKey: ["meeting", numId],
    queryFn: () => meetingsApi.get(numId),
    enabled: !Number.isNaN(numId) && numId > 0,
  });
  return { meeting, isLoading, error, mutate: refetch };
}

export function useSyncCalendar() {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => calendarApi.sync(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      queryClient.invalidateQueries({ queryKey: ["calendar"] });
    },
  });
  return { sync: mutation.mutateAsync, isSyncing: mutation.isPending };
}
