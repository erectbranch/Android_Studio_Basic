# SurfaceView 활용하기


---


## 4.1 SurfaceView(서피스뷰)란?

앞서 View 클래스는 사용자와 상호작용하기 위해 사용했다. 이때 onDraw() 메서드(이미지와 글씨 생성)와 invalidate() 메서드(핸들러를 통한 반복을 위해)를 사용했는데, View 클래스의 일종인 SurfaceView는 이 두 메서드가 필요 없다.

SurfaceView는 다음으로 구성되어 있다.

* Surface: 고속 메모리(버퍼)이며 lockCanvas 메서드에 의해 사용자의 문자나 이미지를 그려지는 곳이다.

* SurfaceHolder: 서피스뷰 전용 인터페이스로, **lockCanvas()**와 **unlockCanvasAndPost()**를 가지고 있다.


### 4.1.2 SurfaceView의 필요성

사용자 인터페이스로 사용하는 쓰레드가 바로 메인 쓰레드인데, 그림을 그리는 작업량이 많다면 쓰레드가 이 작업을 처리하는 바람에 화면 터치에 대한 반응이 잘 이루어지지 않을 수 있다. 이런 문제를 해결하기 위해 메인 쓰레드와 그림을 그리는 쓰레드를 분리할 필요가 있다.

서피스뷰를 사용하면 바로 View에 문자나 이미지를 출력하지 않는다. 그리기 전용으로 분리한 쓰레드에서 고속 메모리인 surface(=버퍼)를 이용해 문자나 이미지를 그려서 한번에 전송한다. 특히 게임과 같이 계속 움직이며 그래픽 처리가 많이 필요할 경우 이렇게 쓰레드를 분리하는 것이 중요하다.


## 4.2 SurfaceHolder 인터페이스

SurfaceHolder는 서피스뷰에서 전용으로 사용하는 인터페이스다. getHolder() 메서드를 이용해서 SurfaceHolder 객체를 얻을 수 있다.

* 메모리(surface)에 그림 및 문자를 그리는 작업을 한다.

* 메모리(surface)에 그린 것들을 사용자 기기 화면으로 복사한다.

```Java
SHolder = getHolder();    // 인터페이스는 직접 객체를 생성할 수 없기 때문에 getHolder() 메서드를 이용해야 한다.
```

캔버스 객체에 drawText와 drawBitmap 메서드를 이용해서 문자와 이미지를 그리기 위해서는 lockCanvas() 메서드를 이용해야 한다. lockCanvas()는 서피스뷰의 캔버스를 사용할 수 있는 권한을 준다.

표시할 내용을 모두 작업했다면, unlockCanvasAndPost() 메서드로 사용자 기기 화면으로 복사할 수 있다.

이런 lockCanvas() 메서드와 unlockCanvasAndPost() 메서드는 쓰레드 클래스의 run() 메서드 안에 적어야 한다. 

SurfaceHolder 인터페이스가 가진 이 두 메서드를 사용하려면, 앞서 얻은 객체(SHolder)에 addCallback 메서드를 사용해 콜백 객체로 등록해야 한다. 이렇게 하면 화면 변화가 발생할 때마다 SurfaceHolder의 콜백 메서드를 호출하게 된다. 

객체를 만들었으면 서피스에 픽셀을 뿌려줄 전용 쓰레드를 만든 뒤, 그 쓰레드에 SHolder 객체를 넘겨주면 된다. 


## 4.3 안드로이드 개발자 API

API란 간단히 말하면 개발자가 사용할 수 있는 함수들의 집합을 의미한다. 

> [SurfaceHolder 설명 문서](https://developer.android.com/reference/android/view/SurfaceHolder.html)

설명 문서에 따르면 SurfaceHolder.Callback 인터페이스를 구현할 때 반드시 구현해야 하는 메서드 3개는 **surfaceChanged, surfaceCreated, surfaceDestoryed** 메서드다. 쓰레드를 실행하는 메서드를 surfaceCreated() 메서드에 넣는다.



---


## 4.4 Thread(쓰레드) 분리하기

쓰레드에 SurfaceView를 연결하려면 다음과 같은 과정을 거쳐야 한다.

1. **서피스뷰를 상속** 받고 **Surface.Callback를 구현**하는 클래스를 만든다.

```Java
public class MySurface extends SurfaceView implements SurfaceHolder.Callback
```


2. 위 클래스에 Thread를 상속 받은 내부 클래스를 만든다.

```Java
    class MyThread extends Thread
```


3. 내부 클래스 멤버 필드에 Thread 객체 및 SurfaceHolder 객체를 선언한다. 

```Java
        MyThread myThread;        // Thread 객체 선언
        SurfaceHolder SHolder;    // SurfaceHolder 객체 선언
```


4. MySurface 클래스의 생성자 안에서 Thread를 생성한다. 이때 생성자 인수로 SurfaceHolder 객체 및 Context 객체를 넘긴다.

```Java
        myThread = new Thread(holder, context);
```


5. surfaceCreated() 메서드 안에 start() 메서드를 넣는다.(Thread를 가동한다.)

```Java
        myThread.start();
```


6. 내부 클래스 안에 run() 메서드를 만들고 다음 내용을 적는다.

```Java
        public void run() {

            Canvas canvas = null;     // 캔버스 객체를 생성한다

            while (true) {            // 계속해서 반복 실행
                canvas = SHolder.lockCanvas();    // 서피스에 문자와 이미지를 그린다.
                
                try {
                    synchronized (SHolder) {
                        drawEverything(canvas);   // 모든 픽셀을 메모리(Surface)에 표현한다.
                    }
                }   finally {
                    if ( canvas != null ) {
                        SHolder.unlockCanvasAndPost(canvas);    // 사용자 화면에 복사한다.
                    }
                }

            }

        }  
```

> [synchronized 개념 정리](https://jgrammer.tistory.com/entry/Java-%ED%98%BC%EB%8F%99%EB%90%98%EB%8A%94-synchronized-%EB%8F%99%EA%B8%B0%ED%99%94-%EC%A0%95%EB%A6%AC)


---


## 4.5 제작할 예제

3장에서 한 바구니 수학게임에 SurfaceView를 적용해 더 발전시킬 것이다. 서브메뉴(덧셈, 뺄셈, 곱셈 선택 / 난이도 선택 / 시간 선택), 배경 음악 추가, 도움말 기능, 정답&오답 개수 표시 기능을 추가한다.

| java 파일 | xml 파일 |
| --- | --- |
| MainActivity.java<br>MySurface | activity_main.xml |

여기에 정답, 오답 풍선 클래스인 AnswerBalloon.java, Balloon.java 파일이 있다.

* MainActivity.java 코드에 사용한 onKeyDown 메서드

```Java
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }


    // 사용자가 키를 누르면 onKeyDown 메서드가 호출된다.
    // 매개변수인 keyCode와 event를 통해 키에 관한 정보를 얻을 수 있다.
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (KeyCode == KeyEvent.KEYCODE_BACK) {    // 이전으로 돌아가기 키를 누르면
            System.exit(0);                        // 단어 공부가 종료된다. (0: 정상 종료)
        }
        return false;    // 리턴값을 false로 하면 onKeyPress 이벤트가 발생하지 않는다.
                         // 따라서 키가 반복해서 입력되는 것을 방지한다.
    }

}
```

* xml에 서피스뷰 등록하기

Activity_main.xml에서 뷰를 사용하는 대신 MySurface 클래스(서피스뷰를 상속 받아 만든 클래스)가 화면에 제시되도록 해야 한다. SurfaceView를 Button이나 TextView처럼 태그를 활용해 레이아웃 안에 넣으면 된다.

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent" >

    <com.example.csc.surfacetest00.MySurface
        android:layout_width="fill_parent"
        android:layout_height="fill_parent"
        />

</LinearLayout>
```

* 효과음 재생하기

배경음악을 재생하려면 MediaPlayer 클래스를 사용한다. 효과음을 위해서는 SoundPool 클래스를 사용한다.

1. (효과음) SoundPool 클래스를 이용하기 위해 sound 객체를 생성한다. 생성자 패러미터는 maxStreams, streamType, srcQuality 순이다. 

| 패러미터 | 설명 |
| --- | --- |
| maxStreams | 미리 로드할 사운드의 스트림 개수 |
| streamType | 게임은 보통 AudioManager.STREAM_ALARM을 사용 |
| srcQuality | 품질 관련 샘플링 값 |

```Java
SoundPool sPool = new SoundPool(1, AudioManager.STREAM_ALARM, 0);
```

2. 사운드를 로드해서 식별자 변수에 넣는다.

```Java
int dingdongdaeng = sPool.load(this, R.raw.dingdongdaeng, 1);
```

load() 메서드의 첫째 패러미터는 Context 객체를 의미한다. 예제에서는 Activity가 Context를 상속 받았으므로 this를 사용한다. 둘째 패러미터는 로드하는 음원 리소스 아이디다. 셋째 패러미터는 우선순위다.

3. 효과음이 나오도록 하는 play 메서드의 패러미터는 다음과 같다. soundID, leftVolumn, rightVolumn, priority, loop, rate다.

```Java
sPool.play(dingdongdaeng, 1, 1, 9, 0, 1);
```

4. (배경음악) MediaPlayer 클래스를 사용한다.

```Java
Mediaplayer backMusic;
backMusic = MediaPlayer.create(this, R.raw.song);
backMusic.setLooping(true);    // 무한 반복 재생
backMusic.start();             // 재생
```

---


## 4.6 예제 코드

```Java
// MySurface.java

package com.erectbranch.mathgame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;
import android.media.AudioManager;
import android.media.SoundPool;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.AttributeSet;
import android.view.Display;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.WindowManager;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.Random;

public class MySurface extends SurfaceView implements SurfaceHolder.Callback {

    // SurfaceView
    MyThread mThread;
    SurfaceHolder mHolder;
    Context mContext;

    // 비트맵
    Bitmap bar;
    Bitmap leftKey, rightKey;
    Bitmap screen;
    Bitmap balloonimg;
    Bitmap resultShow;
    Bitmap menuButton;
    Bitmap helpButton;
    Bitmap closeButton;
    Bitmap applyButton;
    Bitmap plusicon;
    Bitmap minusicon;
    Bitmap multiicon;
    Bitmap time30;
    Bitmap time60;
    Bitmap time120;
    Bitmap level1;
    Bitmap level2;
    Bitmap level3;
    Bitmap scoreImage;
    Bitmap menuTitle;


    // 필드 변수
    int Width, Height;    // 해상도를 받을 변수

    int bar_x, bar_y;     // 바스켓이 있을 좌표
    int barWidth;
    int barHeight;
    int barSpeed;

    int leftKey_x, leftKey_y;
    int rightKey_x, rightKey_y;
    int buttonWidth;      // 버튼 크기

    int score;
    int count = 3000;

    int balloonWidth;
    int balloonHeight;
    int balloonSpeed;

    int oNumber;     // 정답 개수
    int xNumber;     // 오답 개수

    int resultShow_x, resultShow_y;     // 결과보기 이미지 좌표

    int menuOk = 1;                     // 환경 설정이 나오게 하는 변수: 0은 게임 중, 1이면 환경설정 창, 2는 도움말, 3은 결과창

    static final int INGAME = 0;
    static final int SETTING = 1;
    static final int HELPMENU = 2;
    static final int RESULTPOPUP = 3;

    int helpButton_x, helpButton_y;
    int closeButton_x, closeButton_y;
    int applyButton_x, applyButton_y;
    int menuButton_x, menuButton_y;
    int plusicon_x, plusicon_y;
    int minusicon_x, minusicon_y;
    int multiicon_x, multiicon_y;

    int time30_x, time30_y;
    int time60_x, time60_y;
    int time120_x, time120_y;

    int level1_x, level1_y;
    int level2_x, level2_y;
    int level3_x, level3_y;

    int scoreImage_x, scoreImage_y;

    int score_count;
    int scoreImageOk = 0;

    static final int CORRECT = 1;

    int level = 1;        // 난이도 설정 변수: 0 쉬움 1 중간 2 어려움
    int timeValue = 1;    // 시간 설정 변수 : 0 30초 1 1분 2 2분
    int operator;         // 모드 설정 변수 : 0 덧셈 1 뺄셈 2 곱셈

    static final int PLUS_MODE = 0;
    static final int MINUS_MODE = 1;
    static final int MULTI_MODE = 2;

    static final int EASY = 0;
    static final int NORMAL = 1;
    static final int HARD = 2;

    static final int TIME30_MODE = 0;
    static final int TIME60_MODE = 1;
    static final int TIME120_MODE = 2;

    // 문제: number1 + number2 = ?
    // 문제 초기화
    Random random = new Random();
    int number1 = random.nextInt(99) + 1;
    int number2 = random.nextInt(99) + 1;

    int answer = number1 + number2;              // 정답(number1 + number2)

    // 오답
    int[] wrongNumber = new int[] {1,1,1,1,1};   // 초기값 1로 설정

    // 객체 선언
    AnswerBalloon answerBalloon;

    // 풍선이 담긴 ArrayList
    ArrayList<Balloon> balloon;


    // 효과음을 위한 객체 선언
    SoundPool sPool;
    int dingdongdaeng, taeng;


    // 생성자 안에서 쓰레드 생성
    // 이때 생성자 인수로 SurfaceHolder 객체 및 Context 객체를 넘긴다.
    public MySurface(Context context, AttributeSet attrs)  {
        super(context, attrs);
        SurfaceHolder holder = getHolder();     // SurfaceHolder 객체를 생성
        holder.addCallback(this);

        mThread = new MyThread(holder, context);
        InitApp();
        setFocusable(true);
    }


    private void InitApp() {

        // 해상도 값 받아오기
        Display display = ((WindowManager) mContext.getSystemService(Context.WINDOW_SERVICE)).getDefaultDisplay();
        Point size = new Point();
        display.getSize( size );
        Width = size.x;
        Height = size.y;

        // 바 크기
        barWidth = Width / 4;
        barHeight = Height / 14;

        // 버튼 크기
        buttonWidth = Width / 6;

        // 바와 풍선 속도
        barSpeed = Width / 40;
        balloonSpeed = Width / 140;

        // 풍선이 담긴 ArrayList 객체 생성
        balloon = new ArrayList<Balloon>();

        // 비트맵 생성
        bar = BitmapFactory.decodeResource(getResources(), R.drawable.bar);
        leftKey = BitmapFactory.decodeResource(getResources(), R.drawable.leftkey);
        rightKey = BitmapFactory.decodeResource(getResources(), R.drawable.rightkey);
        screen = BitmapFactory.decodeResource(getResources(), R.drawable.screenmath);
        balloonimg = BitmapFactory.decodeResource(getResources(), R.drawable.balloon);
        menuTitle = BitmapFactory.decodeResource(getResources(), R.drawable.menutitle);
        menuButton = BitmapFactory.decodeResource(getResources(), R.drawable.menu);
        helpButton = BitmapFactory.decodeResource(getResources(), R.drawable.help);
        plusicon = BitmapFactory.decodeResource(getResources(), R.drawable.plusicon);
        minusicon = BitmapFactory.decodeResource(getResources(), R.drawable.minusicon);
        multiicon = BitmapFactory.decodeResource(getResources(), R.drawable.multiicon);
        level1 = BitmapFactory.decodeResource(getResources(), R.drawable.level1);
        level2 = BitmapFactory.decodeResource(getResources(), R.drawable.level2);
        level3 = BitmapFactory.decodeResource(getResources(), R.drawable.level3);
        time30 = BitmapFactory.decodeResource(getResources(), R.drawable.time30);
        time60 = BitmapFactory.decodeResource(getResources(), R.drawable.time60);
        time120 = BitmapFactory.decodeResource(getResources(), R.drawable.time120);
        applyButton = BitmapFactory.decodeResource(getResources(), R.drawable.applybutton);
        closeButton = BitmapFactory.decodeResource(getResources(), R.drawable.closebutton);
        scoreImage = BitmapFactory.decodeResource(getResources(), R.drawable.score);
        resultShow = BitmapFactory.decodeResource(getResources(), R.drawable.resultshow);

                // 비트맵 스케일 조정
        bar = Bitmap.createScaledBitmap(bar, barWidth, barHeight, true);
        leftKey = Bitmap.createScaledBitmap(leftKey, buttonWidth, buttonWidth, true);
        rightKey = Bitmap.createScaledBitmap(rightKey, buttonWidth, buttonWidth, true);
        balloonimg = Bitmap.createScaledBitmap(balloonimg, buttonWidth, buttonWidth*5/4, true);
        screen = Bitmap.createScaledBitmap(screen, Width, Height, true);
        menuTitle = Bitmap.createScaledBitmap(menuTitle, Width * 2/5, Height / 7, true);
        menuButton = Bitmap.createScaledBitmap(menuButton, buttonWidth/2, buttonWidth/2, true);
        helpButton = Bitmap.createScaledBitmap(helpButton, buttonWidth, buttonWidth, true);
        plusicon = Bitmap.createScaledBitmap(plusicon, buttonWidth, buttonWidth, true);
        minusicon = Bitmap.createScaledBitmap(minusicon, buttonWidth, buttonWidth, true);
        multiicon = Bitmap.createScaledBitmap(multiicon, buttonWidth, buttonWidth, true);
        level1 = Bitmap.createScaledBitmap(level1, buttonWidth, buttonWidth, true);
        level2 = Bitmap.createScaledBitmap(level2, buttonWidth, buttonWidth, true);
        level3 = Bitmap.createScaledBitmap(level3, buttonWidth, buttonWidth, true);
        time30 = Bitmap.createScaledBitmap(time30, buttonWidth, buttonWidth, true);
        time60 = Bitmap.createScaledBitmap(time60, buttonWidth, buttonWidth, true);
        time120 = Bitmap.createScaledBitmap(time120, buttonWidth, buttonWidth, true);
        applyButton = Bitmap.createScaledBitmap(applyButton, buttonWidth * 4/3, buttonWidth * 3/4, true);
        closeButton = Bitmap.createScaledBitmap(closeButton, buttonWidth * 4/3, buttonWidth * 3/4, true);
        scoreImage = Bitmap.createScaledBitmap(scoreImage, buttonWidth /2, buttonWidth /2, true);
        resultShow = Bitmap.createScaledBitmap(resultShow, Width * 2/3, Height / 3, true);

        // 풍선 크기
        balloonWidth = balloonimg.getWidth();
        balloonHeight = balloonimg.getHeight();

        // 바스켓 초기 좌표
        bar_x = Width / 9;
        bar_y = Height * 2/3;     // 바스켓 초기 좌표

        // 버튼 위치 좌표
        leftKey_x = Width * 5/9;
        leftKey_y = Height * 7/9;

        rightKey_x = Width * 7/9;
        rightKey_y = Height * 7/9;

        menuButton_x = Width - (buttonWidth * 3/2);
        menuButton_y = Height/30;

        helpButton_x = Width - buttonWidth;
        helpButton_y = Height/8;

        plusicon_x = buttonWidth;
        plusicon_y = Height / 5;

        minusicon_x = buttonWidth * 2 + buttonWidth / 4;
        minusicon_y = Height / 5;

        multiicon_x = buttonWidth * 3 + buttonWidth / 2;
        multiicon_y = Height / 5;

        level1_x = plusicon_x;
        level1_y = plusicon_y + buttonWidth * 2;

        level2_x = minusicon_x;
        level2_y = minusicon_y + buttonWidth * 2;

        level3_x = multiicon_x;
        level3_y = multiicon_y + buttonWidth * 2;

        time30_x = plusicon_x;
        time30_y = plusicon_y + buttonWidth * 4;

        time60_x = minusicon_x;
        time60_y = minusicon_y + buttonWidth * 4;

        time120_x = multiicon_x;
        time120_y = multiicon_y + buttonWidth * 4;

        applyButton_x = Width * 1/5;
        applyButton_y = time120_y + buttonWidth * 3/2;

        closeButton_x = Width * 3/5;
        closeButton_y = time120_y + buttonWidth * 3/2;

        resultShow_x = buttonWidth;
        resultShow_y = buttonWidth / 2;

        // 풍선 생성을 위한 랜덤 변수 생성
        Random random = new Random();
        int ran1 = random.nextInt(Width - balloonWidth );

        // 랜덤한 위치에 풍선 생성(랜덤 x 좌표, 꼭대기 y 좌표, 스피드 5)
        answerBalloon = new AnswerBalloon(ran1 + balloonWidth/2, 0, 5);


        // 효과음
        sPool = new SoundPool(10, AudioManager.STREAM_MUSIC, 0);
        dingdongdaeng = sPool.load(mContext, R.raw.dingdongdaeng, 1);
        taeng = sPool.load(mContext, R.raw.taeng, 2);

    }     // end of InitApp()


    // SurfaceHolder.Callback 인터페이스를 구현할 때 반드시 구현해야 하는 메서드 3개
    // surfaceChanged, surfaceCreated, surfaceDestoryed
    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        mThread.start();
    }

    @Override
    public void surfaceChanged(SurfaceHolder arg0, int format, int width, int height) {

    }

    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {

    }

    // ----------------------------
    // MyThread 클래스
    // ----------------------------
    class MyThread extends Thread {

        public MyThread(SurfaceHolder holder, Context context) {
            mHolder = holder;
            mContext = context;
            makeQuestion();
        }

        // ----------------------------
        // drawEverything
        // ----------------------------
        public void drawEverything(Canvas canvas) {

            // 오답 풍선이 5개보다 작으면 오답 풍선을 추가 생성
            if (balloon.size() < 4) {
                Random random = new Random();
                int ran2 = random.nextInt(Width - balloonWidth);

                balloon.add(new Balloon(ran2, 0, 5));    // ArrayList에 새 풍선 추가
            }

            Paint paint1 = new Paint();
            Paint paint2 = new Paint();
            Paint paint3 = new Paint();
            Paint paint4 = new Paint();
            Paint pp = new Paint();

            paint1.setColor(Color.WHITE);
            paint1.setTextSize(Width / 14);

            paint2.setColor(Color.WHITE);
            paint2.setTextSize(Width / 14);
            paint2.setAlpha(100);

            paint3.setColor(Color.BLACK);
            paint3.setTextSize(Width / 12);

            paint4.setColor(Color.BLACK);
            paint4.setTextSize(Width / 14);

            pp.setColor(0xFFFFD9EC);

            canvas.drawRect(0, 0, Width, Height, pp);
            canvas.drawText("남은 시간: " + Integer.toString(count / 50), 0, Height / 7, paint4);
            canvas.drawText("점수: " + Integer.toString(score), 0, Height / 5, paint4);

            // 덧셈 모드(0), 뺄셈 모드(1), 곱셈 모드(2)
            if (operator == PLUS_MODE) {
                answer = number1 + number2;
                canvas.drawText("문제: " + Integer.toString(number1) + "+" + Integer.toString(number2), 0, Height / 13, paint3);
            } else if (operator == MINUS_MODE) {
                answer = number1 - number2;
                canvas.drawText("문제: " + Integer.toString(number1) + "-" + Integer.toString(number2), 0, Height / 13, paint3);
            } else {
                answer = number1 * number2;
                canvas.drawText("문제: " + Integer.toString(number1) + "*" + Integer.toString(number2), 0, Height / 13, paint3);
            }


            // 바스켓이 화면을 벗어날 경우
            if (bar_x < 0) {
                bar_x = 0;
            }
            if (bar_x + barWidth > Width) {
                bar_x = Width - barWidth;
            }


            // 캔버스에 이미지 소스 그리기
            canvas.drawBitmap(screen, 0, 0, paint1);
            canvas.drawBitmap(bar, bar_x, bar_y, paint1);
            canvas.drawBitmap(leftKey, leftKey_x, leftKey_y, paint1);
            canvas.drawBitmap(rightKey, rightKey_x, rightKey_y, paint1);

            // 상단 글씨 표시(점수와 문제)
            canvas.drawText("점수: " + Integer.toString(score), 0, Height / 12, paint1);
            canvas.drawText("문제 : " + Integer.toString(number1) + "+" +
                    Integer.toString(number2), 0, Height / 6, paint1);    // 문제 표시(number1+number2는?)

            // 오답 풍선 그리기
            for (Balloon tmp : balloon) {
                // ArrayList에 있는 풍선들을 그리기
                canvas.drawBitmap(balloonimg, tmp.balloon_x, tmp.balloon_y, paint1);
            }

            // 오답 풍선에 글씨 생성
            for (int i = balloon.size() - 1; i >= 0; i--) {
                // (잘못된 문제[i], 풍선의 x좌표+ 풍선 가로/6, 풍선의 y좌표 + 풍선 세로*2/3, paint)
                canvas.drawText(Integer.toString(wrongNumber[i]), balloon.get(i).balloon_x + balloonWidth / 6,
                        balloon.get(i).balloon_y + balloonHeight * 2 / 3, paint1);
            }


            // 정답 풍선 생성
            canvas.drawBitmap(balloonimg, answerBalloon.balloon_x, answerBalloon.balloon_y, paint1);

            // 정답 풍선에 글씨 생성
            canvas.drawText(Integer.toString(answer), answerBalloon.balloon_x + balloonWidth / 6,
                    answerBalloon.balloon_y + balloonHeight * 2 / 3, paint1);


            // 정답 풍선이 화면 끝에 도달하면
            if (answerBalloon.balloon_y > Height) {
                answerBalloon.balloon_y = 0;     // 다시 꼭대기에서 내려오게 함
            }

            // 게임 중이면 실행되는 코드
            if (menuOk == INGAME) {
                moveBalloon();         // 풍선이 움직인다.
                checkCollision();      // 바스켓과 풍선 충돌 체크
                count--;               // 시간 감소

                canvas.drawBitmap(menuButton, menuButton_x, menuButton_y, paint1);    // 메뉴 버튼 그리기
            }

            // 시간 초과 시 결과창 띄우기
            if (count < 0) {
                menuOk = RESULTPOPUP;
                count = timeValue * 1500 + 1500;    // 30초 60초 120초에 따라 카운트 초기화

                if (timeValue == TIME60_MODE) {
                    count = 6000;
                }

            }


            // 환경설정 메뉴
            if (menuOk == SETTING) {
                canvas.drawRect(0, 0, Width, Height, pp);
                canvas.drawBitmap(menuTitle, 0, 0, paint1);
                canvas.drawText("* 문제유형 선택", buttonWidth, plusicon_y - buttonWidth / 4, paint4);
                canvas.drawBitmap(helpButton, helpButton_x, helpButton_y, paint1);
                canvas.drawBitmap(applyButton, applyButton_x, applyButton_y, paint1);
                canvas.drawBitmap(closeButton, closeButton_x, closeButton_y, paint1);

                // 현재 모드에 따라 아이콘의 투명도를 조절한다
                if (operator == PLUS_MODE) {
                    canvas.drawBitmap(plusicon, plusicon_x, plusicon_y, paint1);
                    canvas.drawBitmap(minusicon, minusicon_x, minusicon_y, paint2);
                    canvas.drawBitmap(multiicon, multiicon_x, multiicon_y, paint2);
                }

                if (operator == MINUS_MODE) {
                    canvas.drawBitmap(plusicon, plusicon_x, plusicon_y, paint2);
                    canvas.drawBitmap(minusicon, minusicon_x, minusicon_y, paint1);
                    canvas.drawBitmap(multiicon, multiicon_x, multiicon_y, paint2);
                }

                if (operator == MULTI_MODE) {
                    canvas.drawBitmap(plusicon, plusicon_x, plusicon_y, paint2);
                    canvas.drawBitmap(minusicon, minusicon_x, minusicon_y, paint2);
                    canvas.drawBitmap(multiicon, multiicon_x, multiicon_y, paint1);
                }

                canvas.drawText("난이도 선택", buttonWidth, level1_y - buttonWidth / 4, paint4);

                if (level == EASY) {
                    canvas.drawBitmap(level1, level1_x, level1_y, paint1);
                    canvas.drawBitmap(level2, level2_x, level2_y, paint2);
                    canvas.drawBitmap(level3, level3_x, level3_y, paint2);
                }

                if (level == NORMAL) {
                    canvas.drawBitmap(level1, level1_x, level1_y, paint2);
                    canvas.drawBitmap(level2, level2_x, level2_y, paint1);
                    canvas.drawBitmap(level3, level3_x, level3_y, paint2);
                }

                if (level == HARD) {
                    canvas.drawBitmap(level1, level1_x, level1_y, paint2);
                    canvas.drawBitmap(level2, level2_x, level2_y, paint2);
                    canvas.drawBitmap(level3, level3_x, level3_y, paint1);
                }

                if (timeValue == TIME30_MODE) {
                    canvas.drawBitmap(time30, time30_x, time30_y, paint1);
                    canvas.drawBitmap(time60, time60_x, time60_y, paint2);
                    canvas.drawBitmap(time120, time120_x, time120_y, paint2);
                }

                if (timeValue == TIME60_MODE) {
                    canvas.drawBitmap(time30, time30_x, time30_y, paint2);
                    canvas.drawBitmap(time60, time60_x, time60_y, paint1);
                    canvas.drawBitmap(time120, time120_x, time120_y, paint2);
                }

                if (timeValue == TIME120_MODE) {
                    canvas.drawBitmap(time30, time30_x, time30_y, paint2);
                    canvas.drawBitmap(time60, time60_x, time60_y, paint2);
                    canvas.drawBitmap(time120, time120_x, time120_y, paint1);
                }

            }

            // 도움말을 나온 화면
            if (menuOk == HELPMENU) {
                canvas.drawRect(0, 0, Width, Height, pp);
                canvas.drawText("바구니를 움직여서", Width / 20, Height / 9, paint3);
                canvas.drawText("정답 풍선을 받는 게임", Width / 20, Height / 4, paint4);
                canvas.drawBitmap(balloonimg, Width / 2, Height / 3, paint1);
                canvas.drawBitmap(bar, Width / 3, Height / 2, paint1);
                canvas.drawBitmap(closeButton, Width /2 - buttonWidth * 2/3, closeButton_y, paint1);
            }

            // 수학게임 결과
            if (menuOk == RESULTPOPUP) {
                canvas.drawRect(0, 0, Width, Height, pp);
                canvas.drawBitmap(resultShow, resultShow_x, resultShow_y, paint1);
                canvas.drawText("맞은 개수: " + oNumber + "개", Width / 10, Height * 9 / 20, paint4);
                canvas.drawText("틀린 개수: " + xNumber + "개", Width / 10, Height / 2, paint4);
                canvas.drawBitmap(closeButton, Width /2 - buttonWidth * 2/3, closeButton_y + buttonWidth / 3, paint1);
            }

            // 정답 풍선을 받았을 경우 화면에 30점 표시하기
            if (scoreImageOk == CORRECT) {
                score_count += 1;

                if (score_count < 40) {
                    canvas.drawBitmap(scoreImage, scoreImage_x, scoreImage_y, paint1);

                } else {
                    score_count = 0;
                    scoreImageOk = 0;
                }

            }


        }    // end of drawEverything


        // 충돌이 일어나면 새 문제를 만든다
        public void makeQuestion() {

            // 정답 풍선에 들어갈 난수 생성
            Random random = new Random();
            int ran1 = random.nextInt(99) + 1;   // 1부터 100까지의 난수 생성
            int ran2 = random.nextInt(99) + 1;

            // 정답 풍선에 들어갈 숫자
            number1 = ran1;
            number2 = ran2;

            if (operator == PLUS_MODE) {
                answer = number1 + number2;     // 정답은 둘의 합
            }

            if (operator == MINUS_MODE) {
                answer = Math.abs(number1 - number2);
            }

            if (operator == MULTI_MODE) {
                int ran4 = random.nextInt(9) + 1;    // 1부터 9까지만
                int ran5 = random.nextInt(9) + 1;

                number1 = ran4;
                number2 = ran5;

                answer = number1 * number2;
            }


            // 오답 풍선에 들어갈 숫자(곱셈)
            if (operator == MULTI_MODE) {
                for (int i = 0; i < wrongNumber.length; i++) {

                    int ran6 = random.nextInt(80) + 1;

                    while (ran6 == answer) {
                        ran6 = random.nextInt(80) + 1;
                    }

                    wrongNumber[i] = ran6;

                }
            } else {    // 오답 풍선에 들어갈 숫자 (덧셈, 뺄셈)

                for (int i = 0; i < wrongNumber.length; i++) {

                    int ran3 = random.nextInt(197) + 1;    // 1부터 정답 아래 수까지

                    while (ran3 == answer) {                      // 만약 랜덤 변수가 정답과 같은 수라면 실행
                        ran3 = random.nextInt(197) + 1;
                    }

                    wrongNumber[i] = ran3;

                }
            }

        }    // end of makeQuestion()


        public void moveBalloon() {

            // 오답 풍선 움직이기
            for (Balloon balloon : balloon) {
                // balloon.move();
                balloon.balloon_y += balloonSpeed;

                // 만약 오답 풍선이 화면 끝에 도달하면 맨 위에서 다시 내려오기
                if (balloon.balloon_y > Height) {
                    balloon.balloon_y = 0;
                }
            }

            // 정답 풍선 움직이기
            // answerBalloon.move();
            answerBalloon.balloon_y += balloonSpeed;

        }    // end of moveBalloon()


        public void checkCollision() {

            // 바스켓에 오답 풍선이 닿으면 적용
            Iterator<Balloon> iterator = balloon.iterator();

            while (iterator.hasNext()) {

                if (collision_x(iterator.next()) && collision_y(iterator.next())) {
                    iterator.remove();    // 풍선을 제거
                    score -= 10;
                    xNumber += 1;    // 틀린 개수 + 1
                    sPool.play(taeng, 1, 1, 9, 0, 1);    // 효과음
                }

            }

            // 바스켓에 정답 풍선이 닿으면 적용
            if (collision_x(answerBalloon) && collision_y(answerBalloon)) {
                score += 30;
                oNumber += 1;       // 맞은 개수 + 1
                makeQuestion();     // 새로운 정답 및 오답 리스트 생성

                // 정답 풍선을 다시 화면 맨 위로
                Random random = new Random();
                answerBalloon.balloon_x = random.nextInt(Width - balloonWidth);
                answerBalloon.balloon_y = 0;

                // 30점 이미지 띄우기
                scoreImageOk = CORRECT;
                scoreImage_x = bar_x - buttonWidth / 2;
                scoreImage_y = bar_y - buttonWidth / 2;

                // 딩동댕 효과음 재생
                sPool.play(dingdongdaeng, 1, 1, 9, 0, 1);

            }


        }    // end of checkCollision

        public boolean collision_x(Balloon balloon) {
            // 바스켓의 시작 x 좌표 < 풍선의 중앙 x 좌표 < 바스켓의 끝 x 좌표
            return ((bar_x < (balloon.balloon_x + balloonWidth / 2)) && ((balloon.balloon_x + balloonWidth / 2) < (bar_x + barWidth)));
        }

        public boolean collision_y(Balloon balloon) {
            // 바스켓의 시작 y 좌표 < 풍선의 중앙 y 좌표 < 바스켓의 끝 y 좌표
            return ((bar_y < (balloon.balloon_y + balloonHeight / 2)) && ((balloon.balloon_y + balloonHeight / 2) < (bar_y + barHeight)));
        }

        public boolean collision_x(AnswerBalloon balloon) {
            // 바스켓의 시작 x 좌표 < 풍선의 중앙 x 좌표 < 바스켓의 끝 x 좌표
            return ((bar_x < (balloon.balloon_x + balloonWidth / 2)) && ((balloon.balloon_x + balloonWidth / 2) < (bar_x + barWidth)));
        }

        public boolean collision_y(AnswerBalloon balloon) {
            // 바스켓의 시작 y 좌표 < 풍선의 중앙 y 좌표 < 바스켓의 끝 y 좌표
            return ((bar_y < (balloon.balloon_y + balloonHeight / 2)) && ((balloon.balloon_y + balloonHeight / 2) < (bar_y + barHeight)));
        }

        // Thread 클래스 run() 메서드 안에 lockCanvas() 메서드와 unlockCanvasAndPost() 메서드를 적어야 한다.
        public void run() {
            Canvas canvas = null;

            while (true) {
                canvas = mHolder.lockCanvas();     // 그림을 메모리에 그린다.

                try {

                    synchronized (mHolder) {
                        drawEverything(canvas);
                    }

                } finally {

                    if (canvas != null) {
                        mHolder.unlockCanvasAndPost(canvas);    // 사용자 화면으로 그림을 전달한다.
                    }

                }
            }    // while

        }    // run

    }    // end of MyThread

    // 사용자가 터치 시 반응 설정
    @Override
    public boolean onTouchEvent (MotionEvent event) {

        int touch_x = 0;
        int touch_y = 0;

        // 사용자가 터치한 부분의 좌표를 가져온다.
        if (event.getAction() == MotionEvent.ACTION_DOWN || event.getAction() == MotionEvent.ACTION_MOVE) {
            touch_x = (int) event.getX();
            touch_y = (int) event.getY();
        }

        // 왼쪽 버튼을 클릭하면
        if ( (touch_x > leftKey_x) && (touch_x < leftKey_x + buttonWidth) &&
                (touch_y > leftKey_y) && (touch_y < leftKey_y + buttonWidth) ) {
            bar_x -= 20;     // 바스켓의 x좌표를 왼쪽으로 옮긴다.
        }

        // 오른쪽 버튼을 클릭하면
        if ( (touch_x > rightKey_x) && (touch_x < rightKey_x + buttonWidth) &&
                (touch_y > rightKey_y) && (touch_y < rightKey_y + buttonWidth) ) {
            bar_x += 20;     // 바스켓의 x좌표를 오른쪽으로 옮긴다.
        }

        // 환경설정 활성화 상태일 경우
        if (menuOk == SETTING) {

            // 덧셈 모드 변경 메뉴 터치
            if ((touch_x > plusicon_x) && (touch_x < plusicon_x + buttonWidth) &&
                    (touch_y > plusicon_y) && (touch_y < plusicon_y + buttonWidth)) {
                operator = PLUS_MODE;
                mThread.makeQuestion();
            }

            // 뺄셈 모드 변경
            if ((touch_x > minusicon_x) && (touch_x < minusicon_x + buttonWidth) &&
                    (touch_y > minusicon_y) && (touch_y < minusicon_y + buttonWidth)) {
                operator = MINUS_MODE;
                mThread.makeQuestion();
            }

            // 곱셈 모드 변경
            if ((touch_x > multiicon_x) && (touch_x < multiicon_x + buttonWidth) &&
                    (touch_y > multiicon_y) && (touch_y < multiicon_y + buttonWidth)) {
                operator = MULTI_MODE;
                mThread.makeQuestion();
            }

            // 시간 변경
            // 30초 모드
            if ((touch_x > time30_x) && (touch_x < time30_x + buttonWidth) &&
                    (touch_y > time30_y) && (touch_y < time30_y + buttonWidth)) {
                count = 50 * 30;
                timeValue = TIME30_MODE;
            }

            // 60초 모드
            if ((touch_x > time60_x) && (touch_x < time60_x + buttonWidth) &&
                    (touch_y > time60_y) && (touch_y < time60_y + buttonWidth)) {
                count = 50 * 60;
                timeValue = TIME60_MODE;
            }

            // 120초 모드
            if ((touch_x > time120_x) && (touch_x < time120_x + buttonWidth) &&
                    (touch_y > time120_y) && (touch_y < time120_y + buttonWidth)) {
                count = 50 * 120;
                timeValue = TIME120_MODE;
            }


            // 난이도 선택
            // 쉬움
            if ((touch_x > level1_x) && (touch_x < level1_x + buttonWidth) &&
                    (touch_y > level1_y) && (touch_y < level1_y + buttonWidth)) {
                level = EASY;
                oNumber = 0;
                xNumber = 0;
                mThread.makeQuestion();
            }

            // 보통
            if ((touch_x > level2_x) && (touch_x < level2_x + buttonWidth) &&
                    (touch_y > level2_y) && (touch_y < level2_y + buttonWidth)) {
                level = NORMAL;
                oNumber = 0;
                xNumber = 0;
                mThread.makeQuestion();
            }

            // 어려움
            if ((touch_x > level3_x) && (touch_x < level3_x + buttonWidth) &&
                    (touch_y > level3_y) && (touch_y < level3_y + buttonWidth)) {
                level = HARD;
                oNumber = 0;
                xNumber = 0;
                mThread.makeQuestion();
            }


            // 환경설정 적용 버튼
            if ((touch_x > applyButton_x) && (touch_x < applyButton_x + buttonWidth*4/3) &&
                    (touch_y > applyButton_y) && (touch_y < applyButton_y + buttonWidth*3/4)) {
                count = timeValue * 1500 + 1500;

                if(timeValue == TIME120_MODE) {
                    count = 6000;
                }

                menuOk = INGAME;

                oNumber = 0;
                xNumber = 0;
            }

            // 환경설정 닫기 버튼
            if ((touch_x > closeButton_x) && (touch_x < closeButton_x + buttonWidth*4/3) &&
                    (touch_y > closeButton_y) && (touch_y < closeButton_y + buttonWidth*3/4)) {
                oNumber = 0;
                xNumber = 0;
                System.exit(0);
            }


            // 환경설정 도움말 버튼
            if ((touch_x > helpButton_x) && (touch_x < helpButton_x + buttonWidth) &&
                    (touch_y > helpButton_y) && (touch_y < helpButton_y + buttonWidth)) {
                menuOk = HELPMENU;
            }

        }    // 환경설정 버튼 상호작용 끝


        // 게임 중 상태에서 버튼 상호작용
        if (menuOk == INGAME) {

            if ((touch_x > menuButton_x) && (touch_x < menuButton_x + buttonWidth/2) &&
                    (touch_y > menuButton_y) && (touch_y < menuButton_y + buttonWidth/2)) {
                menuOk = SETTING;    // 환경설정으로 모드 변경
            }

        }


        // 도움말 닫기 버튼 혹은 결과보기 닫기 버튼
        if (menuOk == HELPMENU || menuOk == RESULTPOPUP) {

            if ((touch_x > Width /2 - buttonWidth * 2/3) && (touch_x < Width /2 + buttonWidth * 2/3) &&
                    (touch_y > closeButton_y +  + buttonWidth / 3) && (touch_y < closeButton_y +  + buttonWidth / 3 + buttonWidth)) {

                if (menuOk == RESULTPOPUP)  {
                    oNumber = 0;
                    xNumber = 0;
                }

                menuOk = SETTING;    // 환경설정으로 모드 변경
            }

        }

        return true;

    }    // end of onTouchEvent


    // ----------------------------
    // onKeyDown
    // ----------------------------
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {

        synchronized (mHolder) {
            switch (keyCode) {
                case KeyEvent.KEYCODE_DPAD_LEFT: break;
                case KeyEvent.KEYCODE_DPAD_RIGHT: break;
                case KeyEvent.KEYCODE_DPAD_UP: break;
            }
        }

        return false;

    }    // end of onKeyDown


}     // end of MySurface
```

아래는 MainActivity.java이다.

```Java
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    // 사용자가 키를 누르면 onKeyDown 메서드가 호출된다.
    // 매개변수인 keyCode와 event를 통해 키에 관한 정보를 얻을 수 있다.
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK) {    // 이전으로 돌아가기 키를 누르면
            System.exit(0);                        // 단어 공부가 종료된다. (0: 정상 종료)
        }
        return false;    // 리턴값을 false로 하면 onKeyPress 이벤트가 발생하지 않는다.
        // 따라서 키가 반복해서 입력되는 것을 방지한다.
    }

}
```

다음은 activity_main.xml 코드다.

```Java
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    >

    <com.erectbranch.mathgame.MySurface
        android:layout_width="fill_parent"
        android:layout_height="fill_parent"
        />

</LinearLayout>
```

Balloon.java와 AnswerBalloon.java는 3장 코드와 동일하다.


---

