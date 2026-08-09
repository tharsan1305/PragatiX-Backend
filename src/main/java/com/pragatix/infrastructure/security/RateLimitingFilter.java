package com.pragatix.infrastructure.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pragatix.common.response.ApiResponse;
import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.Refill;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class RateLimitingFilter extends OncePerRequestFilter {

    private final int authRequestsPerMinute;
    private final int apiRequestsPerMinute;
    private final AuditLogService auditLogService;
    private final ObjectMapper objectMapper;

    private final Map<String, Bucket> authBuckets = new ConcurrentHashMap<>();
    private final Map<String, Bucket> apiBuckets = new ConcurrentHashMap<>();

    public RateLimitingFilter(
            @Value("${security.rate-limit.auth-requests-per-minute:10}") int authRequestsPerMinute,
            @Value("${security.rate-limit.api-requests-per-minute:100}") int apiRequestsPerMinute,
            AuditLogService auditLogService,
            ObjectMapper objectMapper) {
        this.authRequestsPerMinute = authRequestsPerMinute;
        this.apiRequestsPerMinute = apiRequestsPerMinute;
        this.auditLogService = auditLogService;
        this.objectMapper = objectMapper;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain) throws ServletException, IOException {

        String clientIp = IpBlockingFilter.extractClientIp(request);
        String path = request.getRequestURI();

        boolean isAuthRequest = path.startsWith("/api/v1/auth");
        Bucket bucket = isAuthRequest
                ? authBuckets.computeIfAbsent(clientIp, k -> createAuthBucket())
                : apiBuckets.computeIfAbsent(clientIp, k -> createApiBucket());

        if (bucket.tryConsume(1)) {
            filterChain.doFilter(request, response);
        } else {
            auditLogService.logRateLimited(clientIp, request.getRequestURI(), request.getMethod());

            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);

            ApiResponse<Void> apiResponse = ApiResponse.error("Too many requests. Rate limit exceeded. Please try again later.");
            response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
        }
    }

    private Bucket createAuthBucket() {
        Bandwidth limit = Bandwidth.classic(authRequestsPerMinute, Refill.greedy(authRequestsPerMinute, Duration.ofMinutes(1)));
        return Bucket.builder().addLimit(limit).build();
    }

    private Bucket createApiBucket() {
        Bandwidth limit = Bandwidth.classic(apiRequestsPerMinute, Refill.greedy(apiRequestsPerMinute, Duration.ofMinutes(1)));
        return Bucket.builder().addLimit(limit).build();
    }
}
