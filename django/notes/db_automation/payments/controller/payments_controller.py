from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status

from payments.service.payments_service_impl import PaymentsServiceImpl
from redis_cache.service.redis_cache_service_impl import RedisCacheServiceImpl


class PaymentsController(viewsets.ViewSet):
    redisCacheService = RedisCacheServiceImpl.getInstance()
    paymentsService = PaymentsServiceImpl.getInstance()

    def requestProcessPayments(self, request):
        postRequest = request.data
        userToken = postRequest.get("userToken")

        if not userToken:
            return JsonResponse({"error": "userToken이 필요합니다", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # userToken으로 계정 정보 조회
            accountId = self.redisCacheService.getValueByKey(userToken)
            if not accountId:
                return JsonResponse(
                    {"error": "유효하지 않은 userToken입니다", "success": False},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # paymentKey, orderId, amount와 같은 결제 정보 받아옴
            paymentKey = postRequest.get("paymentKey")
            orderId = postRequest.get("orderId")
            amount = postRequest.get("amount")

            if not paymentKey or not orderId or not amount:
                return JsonResponse(
                    {"error": "paymentKey, orderId, amount는 필수입니다.", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 결제 처리
            paymentResult = self.paymentsService.process(accountId, paymentKey, orderId, amount)

            if paymentResult is not None and isinstance(paymentResult, dict):
                # 결제 성공 시 결제 URL과 ID 반환
                paymentUrl = paymentResult.get("receipt", {}).get("url", None)  # receipt URL을 받아옴
                paymentsId = paymentResult.get("paymentKey", None)  # paymentKey를 결제 ID로 사용

                if paymentUrl and paymentsId:
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "결제가 성공적으로 처리되었습니다.",
                            "paymentUrl": paymentUrl,  # 결제 URL
                            "paymentsId": paymentsId,  # 결제 ID
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return JsonResponse(
                        {"error": "결제 URL 또는 결제 ID를 찾을 수 없습니다", "success": False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            else:
                return JsonResponse(
                    {"error": "결제 처리 중 오류 발생", "success": False},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            # 서버 내부 오류 처리
            print(f"주문 처리 중 오류 발생: {e}")
            return JsonResponse(
                {"error": "서버 내부 오류", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )