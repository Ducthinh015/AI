from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from .services import DraughtsGame

game = DraughtsGame()

@api_view(['GET'])
@permission_classes([AllowAny])
def init_board(request):
    board = game.init_board()
    if board is None:
        return Response({"error": "Không thể khởi tạo bàn cờ."},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response({'board': board})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_moves(request):
    position = request.query_params.get('position')
    moves = game.get_valid_moves(position)
    return Response({'moves': moves})

@api_view(['POST'])
@permission_classes([AllowAny])
def make_move(request):
    from_pos = request.data.get('from') or request.data.get('from_pos')
    to_pos   = request.data.get('to')   or request.data.get('to_pos')

    if not from_pos or not to_pos:
        return Response({"error": "Thiếu 'from' hoặc 'to' trong dữ liệu gửi."},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        result = game.make_move(from_pos, to_pos)
        if isinstance(result, dict) and result.get("error"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
    except IndexError:
        return Response({"error": "Vị trí nằm ngoài phạm vi bàn cờ."},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Lỗi không xác định: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AIMoveAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """
        Trả về nước đi AI cho game có id=pk.
        """
        try:
            # Giả sử bạn có method get_ai_move trong DraughtsGame
            ai_move = game.get_ai_move(pk)
            return Response({'ai_move': ai_move})
        except AttributeError:
            return Response(
                {'error': 'Service get_ai_move chưa được triển khai.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Lỗi khi lấy nước đi AI: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
