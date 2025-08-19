import javax.crypto.Cipher;

public class TruePosTest1 {
    public static void main(String[] args) throws Exception {
        // Scenario: Direct string literal matching "IDEA.*"
        // TARGET START
        Cipher.getInstance("IDEA/CBC/PKCS5Padding");
        // TARGET END
   }
}

public class CustomException extends RuntimeException{
    //TARGET_START
    final String customValue;
    //TARGET_END
}

public class Foo {
    public void bar(int a) {
        // TARGET_START
        if (a > 8) {}
        // TARGET_END
    }
}

public class Case1 {
    public void foo() {
        // TARGET_START
        doSomething();
        // TARGET_END
    }

    private static void doSomething() {}
}

// 原始：
 if (lPreparedStmt != null) {...}

// 等价变换后：
import static java.util.Objects.*;
if (Objects.nonNull(lPreparedStmt)) {...}

if (lPreparedStmt == null) return;
...
